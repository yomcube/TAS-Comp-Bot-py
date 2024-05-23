import discord
from discord.ext import commands
from utils import connect_tasks
import sqlite3

class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    async def command(self, ctx, number: int, year: int):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        try: # See if we had connected task or not.
            cursor.execute(f"INSERT INTO tasks VALUES ({number}, {year}, 1)")

        except sqlite3.OperationalError:
            connect_tasks()
            cursor.execute(f"INSERT INTO tasks VALUES ({number}, {year}, 1)")
            await ctx.send("Task was not connected. It has been done for you. Task has been started")

        await ctx.send(f"Starting task {number} in {year}...")

async def setup(bot) -> None:
    await bot.add_cog(Start(bot))