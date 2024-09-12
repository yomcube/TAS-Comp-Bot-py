import discord
import shared
import time
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks

from api.submissions import get_logs_channel
from commands.db.requesttask import check_speed_task_deadlines, check_speed_task_reminders
from api.utils import is_task_currently_running, get_tasks_channel, get_announcement_channel
from api.db_classes import get_session, Tasks, SpeedTaskDesc, SpeedTaskLength
from sqlalchemy import select, update, delete

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

host_role_id = None

"""This file consists of bot tasks that start to run as soon as the bot starts. Most of those tasks run every minute."""


####################################################
# Release speed task at appropriate time
####################################################

@tasks.loop(seconds=60)
async def release_speed_task(bot):
    async with get_session() as session:
        # Only check if we need to release speed task if a speed task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        # Return if not a speed task
        if ongoing_task[4] is None:
            return

        # if speed task already public (towards the end), return
        is_released = ongoing_task[7]
        if is_released:
            return

        # Get speed task general deadline (in UNIX) and speed task length (in hours)
        deadline = ongoing_task[6]

        # Fetch the speed task length in hours and convert it to seconds
        query = await session.execute(select(SpeedTaskLength).where(SpeedTaskLength.comp == DEFAULT))
        length = query.scalars().first()


        task_length_seconds = length.time * 3600

        # Get the current time rounded to the nearest minute
        current_time = int(time.time())


        if (current_time >= (deadline - task_length_seconds)) and not is_released:
            # Get tasks channel
            tasks_channel = await get_tasks_channel(DEFAULT)
            channel = bot.get_channel(tasks_channel)


            # Get speed task description and send it
            query2 = select(SpeedTaskDesc.desc).where(SpeedTaskDesc.comp == DEFAULT)
            task_desc = (await session.scalars(query2)).first()
            task_num = ongoing_task[0]
            year = ongoing_task[1]
            deadline = ongoing_task[6]

            await channel.send(f"__**Task {task_num}, {year}**:__\n\n{task_desc}\n\nYou have until <t:{deadline}:f> "
                               f"(<t:{deadline}:R>) to submit.")

            # Also send an announcement in announcement channel
            announcement_channel = bot.get_channel(await get_announcement_channel(DEFAULT))
            await announcement_channel.send(f"@ everyone Task {task_num} has been released publicly! You have until "
                                      f"<t:{deadline}:R> to submit to this speed task! Please see <#{tasks_channel}> "
                                      f"for task information.")




            # set the task to released; everyone may submit, and bot won't publish task again
            await session.execute(update(Tasks).values(is_released=1).where(Tasks.is_active == 1))

            await session.commit()





@release_speed_task.before_loop
async def before_release_task():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)


####################################################
# Automatically close tasks after deadline
####################################################

@tasks.loop(seconds=60)
async def check_task_deadline(bot):
    async with get_session() as session:

        # Only check deadlines if a task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        # If deadline is none, don't try to auto close task
        if ongoing_task[6] is None:
            return

        load_dotenv()
        DEFAULT = os.getenv('DEFAULT')

        log_channel = bot.get_channel(await get_logs_channel(DEFAULT))
        announcement_channel = bot.get_channel(await get_announcement_channel(DEFAULT))

        # Get the current time rounded to the nearest minute
        current_time = int(time.time())

        # Query for all active tasks with deadlines
        result = await session.execute(
            select(Tasks).where(Tasks.deadline <= current_time, Tasks.is_active == True)
        )
        tasks_to_update = result.scalars().all()

        # stop task
        for _ in tasks_to_update:
            stmt = (
                update(Tasks)
                .where(Tasks.is_active == 1)
                .values(is_active=0)
            )

        try:  # Ending task if we pass deadline
            await session.execute(stmt)
            await session.commit()

            # Delete task
            await session.execute(delete(Tasks).where(Tasks.is_active == 0))
            await session.execute(delete(SpeedTaskDesc))
            await session.commit()

            await log_channel.send("The task has been closed automatically; deadline has passed.")
            await announcement_channel.send(f"Task {ongoing_task[0]} is over! Thank you to everyone who participated!")


        # if we get here, there is no task that needed to be stopped
        except UnboundLocalError:
            pass


@check_task_deadline.before_loop
async def before_check_deadline():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global detected_guild
        detected_guild = None

    @commands.Cog.listener()
    async def on_ready(self):
        shared.main_guild = self.bot.guilds[0]
        print(f"Detected main server: {shared.main_guild.name} (ID: {shared.main_guild.id})")

        check_task_deadline.start(self.bot)
        check_speed_task_deadlines.start(self.bot)

        release_speed_task.start(self.bot)

        check_speed_task_reminders.start(self.bot)


async def setup(bot):
    await bot.add_cog(Ready(bot))
