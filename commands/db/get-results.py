import discord
from discord.ext import commands
import sqlite3
from utils import float_to_readable
from api.submissions import get_display_name

class Results(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-results", description="Get the ordered results", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        
        # Get current task
        cursor.execute("SELECT * FROM submissions LIMIT 1")
        result = cursor.fetchone()
        active_task = result[0]
        
        # Get all submissions ordered by time
        cursor.execute("SELECT * FROM submissions WHERE task = ? ORDER BY time ASC", (active_task,))
        submissions = cursor.fetchall()


        connection.close()
        
        content = f"**__Task {active_task} Results__**:\n\n"
        
        # Add lines in time order
        for (n, submission) in enumerate(submissions, start=1):
            if submission[5]: # dq
                continue
            display_name = get_display_name(submission[2])
            readable_time = float_to_readable(submission[4])
            content += f'{n}. {display_name} — {readable_time}\n'

        await ctx.send(content)


async def setup(bot) -> None:
    await bot.add_cog(Results(bot))
