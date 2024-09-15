import os
import discord
import shared
from discord.ext import commands, tasks
from api.utils import is_task_currently_running, get_submitter_role, get_announcement_channel, get_tasks_channel
from api.db_classes import SpeedTaskDesc, SpeedTaskLength, SpeedTaskReminders, SpeedTask, get_session, ReminderPings
from sqlalchemy import select, insert, update
from dotenv import load_dotenv
import math
import time
import asyncio

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


# Credits to original sm64 / mkw tas comp bot (by Xander) for messages


async def has_requested_already(id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask)
                                        .where(SpeedTask.user_id == id))).first()
        return result


async def is_time_over(id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask.active)
                                        .where(SpeedTask.user_id == id))).first()

        if result is None: # this happens when they are doing the task after it has been revealed; towards the end
            return False


        return int(result[0]) == 0


async def get_end_time(task_duration):
    """Returns the UNIX timestamp of the user's end of task time"""
    duration_seconds = task_duration * 3600
    end_time = time.time() + duration_seconds

    rounded_time = round(end_time)

    rounded_time_to_minute = math.ceil(rounded_time / 60) * 60

    return rounded_time_to_minute


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
            return await ctx.send(f"The task has already been posted publicly! Please see <#{tasks_channel}> for task information.")

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
