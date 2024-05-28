import discord
from discord.ext import commands
import sqlite3


class End(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="end-task", description="End current task", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Is a task running?
        cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
        currently_running = cursor.fetchone()


        if currently_running:
            number = currently_running[0]
            year = currently_running[1]

            cursor.execute("UPDATE tasks SET is_active = 0 WHERE is_active = 1")

            connection.commit()  # actually update the database
            connection.close()
            
            await ctx.send(f"Successfully ended **Task {number} - {year}**!")
        else:
            await ctx.send(f"There is already no ongoing task!")


async def setup(bot) -> None:
    await bot.add_cog(End(bot))