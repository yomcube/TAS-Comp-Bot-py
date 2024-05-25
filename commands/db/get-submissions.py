import discord
from discord.ext import commands
import sqlite3

class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        
        # Get current task
        cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
        active_task = cursor.fetchone()
        
        if not active_task:
            await ctx.reply(f"There is no ongoing task!\nUse `/start-task` to start a new task.")
            return  # Early return if there's no active task
        
        # Get submissions from current task
        cursor.execute("SELECT * FROM submissions WHERE task = ?", (active_task[0],))
        submissions = cursor.fetchall()  # Fetch all rows
        
        # Count submissions from current task
        cursor.execute("SELECT COUNT(*) FROM submissions WHERE task = ?", (active_task[0],))
        total_submissions = cursor.fetchone()[0]  # Get the count
        
        connection.close()
        
        embed = discord.Embed(
            title=f"Task {active_task[0]} - {active_task[1]} submissions",
            description=f"Total submissions: {total_submissions}"
        )
        
        # Add many fields depending on the number of submissions
        for submission in submissions:
            if submission[5] == 0:
                dq = False
            elif submission[5] == 1:
                dq = True
                
            embed.add_field(name="Submission ID", value=f"{submission[0]}", inline=True)
            embed.add_field(name="User", value=f"{submission[1]}", inline=True)
            embed.add_field(name="URL", value=f"{submission[3]}", inline=True)
            embed.add_field(name="Time", value=f"{submission[4]}", inline=True)
            embed.add_field(name="DQ", value=f"{dq}", inline=True)
        
        await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Get(bot))
