import os
import discord
from discord.ext import commands, tasks
from api.utils import is_task_currently_running
from api.db_classes import SpeedTaskDesc, SpeedTaskTime, SpeedTask, get_session
from sqlalchemy import select, insert, update
from dotenv import load_dotenv
import math
import time
import asyncio

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

async def has_requested_already(id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask)
                                        .where(SpeedTask.user_id == id))).first()
        return result

async def is_time_over(id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask.active)
                                        .where(SpeedTask.user_id == id))).first()

        return int(result[0]) == 0




async def get_end_time(task_duration):
    """Returns the UNIX timestamp of the user's end of task time"""
    duration_seconds = task_duration * 3600
    end_time = time.time() + duration_seconds

    rounded_time = round(end_time)

    rounded_time_to_minute = math.ceil(rounded_time / 60) * 60

    return rounded_time_to_minute


@tasks.loop(seconds=60)
async def check_deadlines(bot):
    async with get_session() as session:

        # Only check deadlines if a speed task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        if not ongoing_task[4]:
            return

        # Check if the table is empty
        result = await session.execute(select(SpeedTask))
        tasks_list = result.scalars().all()  # Fetch all tasks into a list

        task_count = len(tasks_list)  # Get the count of tasks

        # Only check deadlines once people have started requesting tasks
        if task_count == 0:
            return

        # Get the current time rounded to the nearest minute
        current_time = int(time.time())

        # Query for all active tasks with deadlines
        result = await session.execute(
            select(SpeedTask).where(SpeedTask.end_time <= current_time, SpeedTask.active == True)
        )
        tasks_to_update = result.scalars().all()

        for task in tasks_to_update:
            stmt = (
                update(SpeedTask)
                .where(SpeedTask.user_id == task.user_id)  # Ensure we update based on user_id
                .values(active=0)
            )
            await session.execute(stmt)
            await session.commit()

            user = bot.get_user(task.user_id)
            await user.send("Your time for this competition is over! Your deadline has passed.")

@check_deadlines.before_loop
async def before_check_deadlines():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)

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