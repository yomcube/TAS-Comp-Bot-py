import discord
from discord.ext import commands
import sqlite3
from api.submissions import get_display_name

class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Get current task
        cursor.execute("SELECT * FROM submissions LIMIT 1")
        result = cursor.fetchone()
        active_task = result[0]


        
        # Get submissions from current task
        cursor.execute("SELECT * FROM submissions WHERE task = ?", (active_task,))
        submissions = cursor.fetchall()  # Fetch all rows
        
        # Count submissions from current task
        cursor.execute("SELECT COUNT(*) FROM submissions WHERE task = ?", (active_task,))
        total_submissions = cursor.fetchone()[0]  # Get the count
        
        connection.close()

        content = f"__Task {active_task} submissions__:\n(Total submissions: {total_submissions})\n\n"

        # Add many lines depending on the number of submissions
        for submission in submissions:
            content += f"{get_display_name(submission[2])} : {submission[3]} | Fetched time: {submission[4]}\n"

        await ctx.reply(content=content)

async def setup(bot) -> None:
    await bot.add_cog(Get(bot))
