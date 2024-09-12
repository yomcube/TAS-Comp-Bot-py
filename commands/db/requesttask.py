import os
import discord
import shared
from discord.ext import commands, tasks
from api.utils import is_task_currently_running, get_submitter_role, get_announcement_channel, get_tasks_channel
from api.db_classes import SpeedTaskDesc, SpeedTaskLength, SpeedTaskReminders, SpeedTask, get_session
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

                            await announcement_channel.send(
                                f"Reminder: You have {time_str} remaining to submit!"
                            )


@check_speed_task_reminders.before_loop
async def before_check_reminders():
    # Wait until the start of the next minute
    now = time.time()
    seconds_until_next_minute = 60 - (int(now) % 60)
    await asyncio.sleep(seconds_until_next_minute)


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

            user = bot.get_user(task.user_id)
            await user.send(f"Your time is up! Thank you for participating in Task {ongoing_task[0]}.")

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
