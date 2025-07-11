import math
import time

from sqlalchemy import select

from api.db_classes import SpeedTask, get_session


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