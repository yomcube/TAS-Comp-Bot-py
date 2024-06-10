from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv
from datetime import date
from api.utils import is_task_currently_running, has_host_role, session
from api.submissions import get_submission_channel
from api.db_classes import Tasks, Submissions
from sqlalchemy import insert, delete

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, year: int = None, collab: int = 0, multiple_tracks: int = 0,
                      speed_task: int = 0):

        if not year:
            year = date.today().year

        if is_task_currently_running() is None:

            # Mark task as ongoing
            session.execute(insert(Tasks).values(number=number, year=year, is_active=1, collab=collab,
                                                 multiple_tracks=multiple_tracks, speed_task=speed_task))

            # Clear submissions from previous task
            session.execute(delete(Submissions))
            # Commit changes to both tables affected
            session.commit()

            # Delete previous "Current submissions" message in submission channel
            channel_id = get_submission_channel(DEFAULT)
            channel = self.bot.get_channel(channel_id)

            try:
                async for message in channel.history(limit=5):  # Adjust limit as necessary
                    if message.author == self.bot.user:
                        await message.delete()
                        break

            except AttributeError:
                await ctx.send(
                    "Please set the submission channel with `/set-submission-channel`! (Ask an admin if you do not "
                    "have permission)")

            await ctx.send(f"Succesfully started **Task {number} - {year}**!")

        else:
            # if a task is already ongoing...
            await ctx.send(f"A task is already ongoing.\nPlease use `/end-task` to end the current task.")
            return


async def setup(bot) -> None:
    await bot.add_cog(Start(bot))
