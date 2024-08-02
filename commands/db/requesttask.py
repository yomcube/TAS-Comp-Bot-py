import os
import discord
from discord.ext import commands
from api.utils import is_task_currently_running
from api.db_classes import SpeedTaskDesc, SpeedTaskTime, SpeedTask, get_session
from sqlalchemy import select, insert
from dotenv import load_dotenv
import time

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

async def has_requested_already(id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask)
                                        .where(SpeedTask.user_id == id))).first()
        return result


async def get_end_time(task_duration):
    """Returns the UNIX timestamp of the user's end of task time"""
    duration_seconds = task_duration * 3600
    end_time = time.time() + duration_seconds

    rounded_time = round(end_time)

    return rounded_time


class Requesttask(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="requesttask")
    async def requesttask(self, ctx):

        current_task = await is_task_currently_running()

        # if not speed task
        if not current_task[4]:
            return await ctx.send("This is not a speed task! The task is posted publicly already.")

        if await has_requested_already(ctx.author.id):
            return await ctx.send("You have already requested the task.")



        async with get_session() as session:
            query = select(SpeedTaskDesc.desc).where(SpeedTaskDesc.guild_id == ctx.guild.id)
            task_desc = (await session.scalars(query)).first()

            query2 = select(SpeedTaskTime.time).where(SpeedTaskTime.guild_id == ctx.guild.id)
            task_duration = (await session.scalars(query2)).first()

            task_number = current_task[0]
            task_year = current_task[1]

            end_time = await get_end_time(task_duration)



            try:
                await ctx.author.send(f"You have requested the task!\n\n**__Task {task_number}, {task_year}:__** \n\n{task_desc}\n\n"
                                      f"You have until <t:{end_time}:f> (<t:{end_time}:R>) to submit.\nGood luck!")

            except discord.Forbidden: # Catch DM closed error
                return await ctx.send("I couldn't send you a DM. Do you have DMs disabled?")

            await session.execute(insert(SpeedTask).values(user_id=ctx.author.id, end_time=end_time, active=1))

            await session.commit()



async def setup(bot) -> None:
    await bot.add_cog(Requesttask(bot))
