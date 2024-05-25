import discord
from discord.ext import commands
import sqlite3

class Results(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-results", description="Get the ordered results", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        
        # Get current task
        cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
        active_task = cursor.fetchone()
        
        if not active_task:
            await ctx.reply(f"There is no ongoing task!\nUse `/start-task` to start a new task.")
            return  # Early return if there's no active task
        
        # Get all submissions ordered by time
        cursor.execute("SELECT * FROM submissions WHERE task = ? ORDER BY time ASC", (active_task[0],))
        submissions = cursor.fetchall()
        
        connection.close()
        
        content = f"**__Task {active_task[0]} Results__**:\n\n"
        
        # Add lines in time order
        for submission in submissions:
            if submission[5] == 0:
                dq = False
            elif submission[5] == 1:
                dq = True
            # put 1st, 2nd etc 
            
            
        
        await ctx.reply(content=content)

async def setup(bot) -> None:
    await bot.add_cog(Results(bot))
