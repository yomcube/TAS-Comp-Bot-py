import discord
from discord.ext import commands
import sqlite3
from datetime import date
from utils import is_task_currently_running


class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    async def command(self, ctx, number: int, year: int=None, collab: int = 0, multiple_tracks: int = 0, speed_task: int = 0):

        if not year:
            year = date.today().year

        if not is_task_currently_running():
            connection = sqlite3.connect("database/tasks.db")
            cursor = connection.cursor()

            # Mark task as ongoing
            cursor.execute(f"INSERT INTO tasks VALUES ({number}, {year}, 1, {collab}, {multiple_tracks}, {speed_task})")

            # Clear submissions from previous task
            cursor.execute("DELETE FROM submissions")

            # Commit changes to both tables affected
            connection.commit()
            connection.close()


            await ctx.send(f"Succesfully started **Task {number} - {year}**!")

        else:
            # if a task is already ongoing...
            await ctx.send(f"A task is already ongoing.\nPlease use `/end-task` to end the current task.")
            return


async def setup(bot) -> None:
    await bot.add_cog(Start(bot))