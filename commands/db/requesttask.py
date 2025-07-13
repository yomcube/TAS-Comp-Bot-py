import os

import discord
import shared
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, insert

from api.db_classes import SpeedTaskDesc, SpeedTaskLength, SpeedTask, get_session
from api.task_handling import has_requested_already, get_end_time, is_task_currently_running
from api.utils import get_tasks_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


# Credits to original sm64 / mkw tas comp bot (by Xander) for messages

class Requesttask(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="requesttask")
    async def requesttask(self, ctx):

        current_task = await is_task_currently_running()

        if current_task is None:
            return await ctx.send("There is no active speed task yet.")

        # if not speed task
        if not current_task[4]:
            tasks_channel = await get_tasks_channel(DEFAULT)
            return await ctx.send(f"This is not a speed task! Please see <#{tasks_channel}> for task information.")

        if await has_requested_already(ctx.author.id):
            return await ctx.send("You have already requested the task.")

        # if task is released, but try to requets task
        if current_task[7]:
            tasks_channel = await get_tasks_channel(DEFAULT)
            return await ctx.send(
                f"The task has already been posted publicly! Please see <#{tasks_channel}> for task information.")

        async with get_session() as session:

            # use shared.main_guild.id to be able to use the command both in server, and in DM (where guild is None)
            query = select(SpeedTaskDesc.desc).where(SpeedTaskDesc.guild_id == shared.main_guild.id)
            task_desc = (await session.scalars(query)).first()

            query2 = select(SpeedTaskLength.time).where(SpeedTaskLength.guild_id == shared.main_guild.id)
            task_duration = (await session.scalars(query2)).first()

            task_number = current_task[0]
            task_year = current_task[1]

            end_time = await get_end_time(task_duration)

            try:
                await ctx.author.send(
                    f"You have requested the task!\n\n**__Task {task_number}, {task_year}:__** \n\n{task_desc}\n\n"
                    f"You have until <t:{end_time}:f> (<t:{end_time}:R>) to submit.\nGood luck!")

            except discord.Forbidden:  # Catch DM closed error
                return await ctx.send("I couldn't send you a DM. Do you have DMs disabled?")

            await session.execute(insert(SpeedTask).values(user_id=ctx.author.id, end_time=end_time, active=1))

            await session.commit()


async def setup(bot) -> None:
    await bot.add_cog(Requesttask(bot))
