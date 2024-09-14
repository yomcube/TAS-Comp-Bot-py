import discord
import shared
import time
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks

from api.submissions import get_logs_channel
from api.utils import is_task_currently_running, get_tasks_channel, get_announcement_channel, get_submitter_role
from api.db_classes import get_session, Tasks, SpeedTaskDesc, SpeedTaskLength, ReminderPings, SpeedTaskReminders, \
    SpeedTask, Submissions
from sqlalchemy import select, update, delete, insert

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
            await announcement_channel.send(f"@everyone Task {task_num} has been released publicly! You have until "
                                      f"<t:{deadline}:t> (<t:{deadline}:R>) to submit to this speed task! "
                                      f"Please see <#{tasks_channel}> for task information.")




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


import os

from dotenv import load_dotenv
import shared
import time
import asyncio
from discord.ext import commands, tasks

from api.submissions import get_logs_channel
from commands.db.requesttask import check_speed_task_deadlines
from api.utils import is_task_currently_running
from api.db_classes import  get_session, Tasks
from sqlalchemy import select, update, delete

host_role_id = None


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
        try: # Ending task if we pass deadline

            await session.execute(stmt)
            await session.commit()

            # Delete task
            await session.execute(delete(Tasks).where(Tasks.is_active == 0))

            await session.execute(delete(SpeedTaskDesc))
            await session.commit()

            await log_channel.send("The task has been closed automatically; deadline has passed.")
            await announcement_channel.send(f"Task {ongoing_task[0]} is over! Thank you to everyone who participated!")


            await session.commit()

            await log_channel.send("The task has been closed automatically; deadline has passed.")


        # if we get here, there is no task that needed to be stopped
        except UnboundLocalError:
            pass


@check_task_deadline.before_loop
async def before_check_deadline():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)


####################################################
# Check for reminders in speed tasks
####################################################
@tasks.loop(seconds=60)
async def check_speed_task_reminders(bot):
    async with get_session() as session:

        # Only check reminders if a speed task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        if not ongoing_task[4]:
            return

        # Get the current time
        current_time = int(time.time())

        # Query all users with active tasks
        result = await session.execute(select(SpeedTask).where(SpeedTask.active == True))
        active_tasks = result.scalars().all()

        for task in active_tasks:
            # Query reminders for this guild
            reminder_query = select(SpeedTaskReminders).where(SpeedTaskReminders.comp == DEFAULT)
            reminder_result = await session.execute(reminder_query)
            reminders = reminder_result.scalar_one_or_none()

            if reminders:
                # Calculate the time left for the task
                time_left = task.end_time - current_time

                # Send reminders based on the time left
                for reminder in [reminders.reminder1, reminders.reminder2, reminders.reminder3, reminders.reminder4]:
                    if reminder is not None and time_left == reminder * 60:  # Convert reminder from minutes to seconds
                        hours = reminder // 60
                        minutes = reminder % 60

                        # Handle exactly 60 minutes as 1 hour
                        if reminder == 60:
                            time_str = "1 hour"
                        else:
                            time_str = ""
                            if hours > 0:
                                hour_unit = "hour" if hours == 1 else "hours"
                                time_str = f"{hours} {hour_unit}"

                            if minutes > 0:
                                minute_unit = "minute" if minutes == 1 else "minutes"
                                if time_str:
                                    time_str += f" and {minutes} {minute_unit}"
                                else:
                                    time_str = f"{minutes} {minute_unit}"
                        user = bot.get_user(task.user_id)
                        if user:
                            await user.send(f"You have {time_str} remaining to submit!")

        # Also do public reminders is task is released
        if ongoing_task[7]:
            reminder_query = select(SpeedTaskReminders).where(SpeedTaskReminders.comp == DEFAULT)
            reminder_result = await session.execute(reminder_query)
            reminders = reminder_result.scalar_one_or_none()

            if reminders:
                announcement_channel = bot.get_channel(await get_announcement_channel(DEFAULT))
                deadline = ongoing_task[6]
                time_left = deadline - current_time

                if announcement_channel:
                    for reminder in [reminders.reminder1, reminders.reminder2, reminders.reminder3,
                                     reminders.reminder4]:
                        if reminder is not None and time_left == reminder * 60:  # Convert reminder from minutes to seconds
                            hours = reminder // 60
                            minutes = reminder % 60

                            # Handle exactly 60 minutes as 1 hour
                            if reminder == 60:
                                time_str = "1 hour"
                            else:
                                time_str = ""
                                if hours > 0:
                                    hour_unit = "hour" if hours == 1 else "hours"
                                    time_str = f"{hours} {hour_unit}"

                                if minutes > 0:
                                    minute_unit = "minute" if minutes == 1 else "minutes"
                                    if time_str:
                                        time_str += f" and {minutes} {minute_unit}"
                                    else:
                                        time_str = f"{minutes} {minute_unit}"

                            # Send reminder (with @everyone ping depending on setting)
                            ping_query = select(ReminderPings.ping).where(ReminderPings.guild_id == shared.main_guild.id)
                            result = (await session.execute(ping_query)).first()

                            if result is None or result[0] == 0:
                                await announcement_channel.send(f"Reminder: You have {time_str} remaining to submit!")
                            else:
                                await announcement_channel.send(f"@everyone Reminder: You have {time_str} remaining to submit!")


@check_speed_task_reminders.before_loop
async def before_check_reminders():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)


####################################################
# Check for individual deadlines in speed tasks
####################################################

@tasks.loop(seconds=60)
async def check_speed_task_deadlines(bot):
    async with get_session() as session:

        # Only check deadlines if a speed task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        if not ongoing_task[4]:
            return

        # Check if the table is empty
        result = await session.execute(select(SpeedTask))
        user_list = result.scalars().all()  # Fetch all users in a list

        user_count = len(user_list)  # Get the count of users

        # Only check deadlines once people have started requesting tasks
        if user_count == 0:
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

            # Send user a message when their time is up
            user = bot.get_user(task.user_id)
            await user.send(f"Your time is up! Thank you for participating in Task {ongoing_task[0]}")

            # Give the user a role upon their deadline
            guild_id = shared.main_guild.id

            if guild_id is None:
                print("Guild not detected yet.")
                return

            submitter_role = await get_submitter_role(DEFAULT)

            # Fetch the member from the detected guild
            server = bot.get_guild(guild_id)
            member = server.get_member(task.user_id)

            if member:
                role = server.get_role(submitter_role)
                if role:
                    if role not in member.roles:
                        await member.add_roles(role)
                        print(f"Role {role.name} has been assigned to {member.display_name}.")
                else:
                    print(f"Role with ID {submitter_role} not found in this server.")
            else:
                print(f"User with ID {task.user_id} not found in this server.")


@check_speed_task_deadlines.before_loop
async def before_check_deadlines():
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

        # Adding a default setting for reminder pings (only do once):
        async with get_session() as session:
            query = select(ReminderPings.ping).where(ReminderPings.guild_id == shared.main_guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(ReminderPings).values(ping=0, guild_id=shared.main_guild.id, comp=DEFAULT)
                await session.execute(stmt)
                await session.commit()


async def setup(bot):
    await bot.add_cog(Ready(bot))
