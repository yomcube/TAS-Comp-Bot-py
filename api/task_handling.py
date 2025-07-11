import math
import os
import time
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import select, insert, delete, update

from api.db_classes import SpeedTask, get_session, Tasks, SpeedTaskDesc, SpeedTaskLength, SpeedTaskReminders, \
    Submissions, Teams

load_dotenv()
DEFAULT = os.getenv('DEFAULT')
async def is_task_currently_running():
    """Check if a task is currently running. Returns a list with the parameters of active task, if so."""
    # Is a task running?
    async with get_session() as session:
        active = (await session.execute(select(Tasks.task, Tasks.year, Tasks.is_active, Tasks.team_size,
                                               Tasks.speed_task, Tasks.multiple_tracks, Tasks.deadline, Tasks.is_released)
                                        .where(Tasks.is_active == 1))).first()
        return active


async def has_requested_already(user_id):
    async with get_session() as session:
        result = (await session.execute(select(SpeedTask)
                                        .where(SpeedTask.user_id == user_id))).first()
        return result


async def is_time_over(user_id):
    async with get_session() as session:
        result = (await session.scalars(select(SpeedTask.active)
                                        .where(SpeedTask.user_id == user_id))).first()

        if result is None: # this happens when they are doing the task after it has been revealed; towards the end
            return False

        return int(result) == 0


async def get_end_time(task_duration):
    """Returns the UNIX timestamp of the user's end of task time"""
    duration_seconds = task_duration * 3600
    end_time = time.time() + duration_seconds

    rounded_time = round(end_time)

    rounded_time_to_minute = math.ceil(rounded_time / 60) * 60

    return rounded_time_to_minute

async def start_task(number: int, team_size: int = 1, multiple_tracks: int = 0,
                        speed_task: int = 0, year: int = None, deadline: int = None,
                        guild_id: int = None, message_guild_id: int = None) -> str | bool:
    # auto set year
    if not year:
        year = date.today().year

    if await is_task_currently_running() is None:
        async with get_session() as session:

            #########################################
            # Cases where a task cannot be started
            #########################################
            if deadline is not None:
                # Prevent a task from creating if deadline is in the past
                if deadline < int(time.time()):
                    return "This deadline is in the past! Retry again."

                else:  # if deadline is valid, round it up to nearest minute
                    deadline = math.ceil(deadline / 60) * 60

            # Don't start speed task if no description is set
            if speed_task == 1:
                async with get_session() as session:
                    query = select(SpeedTaskDesc.desc).where(SpeedTaskDesc.guild_id == guild_id)
                    task_desc = (await session.scalars(query)).first()

                    if task_desc is None:
                        return "Please set a speed task description with `$speed-task-desc`!"

                if deadline is None:
                    return ("Speed tasks require a general deadline in order to function properly."
                            " Please set one (with a UNIX timestamp).")

            #########################################
            #
            #########################################

            # Insert task in database. Non speed task case (difference is the is-released parameter)
            if speed_task == 0:
                await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                           multiple_tracks=multiple_tracks, speed_task=speed_task,
                                                           deadline=deadline, is_released=1))


            # Insert task in database. Speed task case
            else:
                await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                           multiple_tracks=multiple_tracks, speed_task=speed_task,
                                                           deadline=deadline, is_released=0))

                # If a speed task and there is no default task duration set, set it to 4h.
                query = select(SpeedTaskLength.time).where(SpeedTaskLength.guild_id == guild_id)
                task_duration = (await session.scalars(query)).first()

                if task_duration is None:
                    stmt = insert(SpeedTaskLength).values(guild_id=message_guild_id, time=4.0, comp=DEFAULT)
                    await session.execute(stmt)
                    await session.commit()

                # Find if the speed task reminders were set
                result = await session.execute(
                    select(SpeedTaskReminders).where(SpeedTaskReminders.guild_id == message_guild_id))
                reminders = result.scalar_one_or_none()

                # Check if all reminder columns are None, if not, set default reminders
                if not reminders:
                    # get task duration
                    query2 = select(SpeedTaskLength.time).where(SpeedTaskLength.guild_id == message_guild_id)
                    task_duration = (await session.scalars(query2)).first()

                    new_task_reminder = SpeedTaskReminders(
                        comp=DEFAULT,
                        reminder1=(task_duration * 60) * 0.5,
                        reminder2=(task_duration * 60) * 0.25,
                        reminder3=10,
                        reminder4=None,
                        guild_id=guild_id
                    )
                    session.add(new_task_reminder)

                    # Commit changes to the database
                    await session.commit()

            # Clear submissions from previous task, as well as potential teams, and speed task table
            await session.execute(delete(Submissions))
            await session.execute(delete(Teams))
            await session.execute(delete(SpeedTask))
            await session.commit()
        return True


    else:
        # if a task is already ongoing...
        return "A task is already ongoing.\nPlease use `/end-task` to end the current task."

async def end_task() -> str:
    async with get_session() as session:
        currently_running = (await session.execute(select(Tasks.task, Tasks.year).where(Tasks.is_active == 1))).first()

    # Is a task running?
    if currently_running:
        async with get_session() as session:

            number = currently_running.task
            year = currently_running.year
            await session.execute(update(Tasks).values(is_active=0).where(Tasks.is_active == 1))

            # Delete the task -- we don't really need to keep, and delete speed task desc
            await session.execute(delete(Tasks).where(Tasks.is_active == 0))
            await session.execute(delete(SpeedTaskDesc))

            await session.commit()

        return f"Successfully ended **Task {number} - {year}**!"
    else:
        return "There is already no ongoing task!"