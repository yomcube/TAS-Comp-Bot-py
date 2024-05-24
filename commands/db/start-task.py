import discord
from discord.ext import commands
import sqlite3


class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    async def command(self, ctx, number: int, year: int, collab: int = 0, multiple_tracks: int = 0, speed_task: int = 0):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Is a task running?
        cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
        currently_running = cursor.fetchone()

        if not currently_running:
            # Mark task as ongoing
            cursor.execute(f"INSERT INTO tasks VALUES ({number}, {year}, 1, {collab}, {multiple_tracks}, {speed_task})")

            # Clear submissions from previous task
            cursor.execute("DELETE FROM submissions")

            # Commit changes to both tables affected
            connection.commit()
            connection.close()


            await ctx.send(f"Starting task {number}, {year}.")

        else:
            # if a task is already ongoing...
            await ctx.send(f"ERROR: A task is already ongoing.")
            return


async def setup(bot) -> None:
    await bot.add_cog(Start(bot))