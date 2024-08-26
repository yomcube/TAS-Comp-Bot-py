import discord
import shared
import time
import asyncio
from discord.ext import commands, tasks
from commands.db.requesttask import check_speed_task_deadlines
from api.utils import is_task_currently_running
from api.db_classes import  get_session, Tasks
from sqlalchemy import select, update, delete

host_role_id = None

@tasks.loop(seconds=60)
async def check_task_deadline():
    async with get_session() as session:

        # Only check deadlines if a task is ongoing
        ongoing_task = await is_task_currently_running()

        if ongoing_task is None:
            return

        # If deadline is none, don't try to auto close task
        if ongoing_task[6] is None:
            return

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

        try: # Ending task if we pass deadline
            await session.execute(stmt)
            await session.commit()

            # Delete task
            await session.execute(delete(Tasks).where(Tasks.is_active == 0))
            await session.commit()

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

        check_task_deadline.start()
        check_speed_task_deadlines.start(self.bot)


async def setup(bot):
    await bot.add_cog(Ready(bot))
