from discord.ext import commands
import sqlite3
from api.submissions import get_display_name
from api.utils import has_host_role, float_to_readable

class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Get current task by taking random submission, and extracting task number
        cursor.execute("SELECT * FROM submissions LIMIT 1")
        result = cursor.fetchone()

        try:
            active_task = result[0]

        except TypeError:
            await ctx.send("There were no submissions.")
            return


        
        # Get submissions from current task
        cursor.execute("SELECT * FROM submissions WHERE task = ?", (active_task,))
        submissions = cursor.fetchall()  # Fetch all rows
        
        # Count submissions from current task
        cursor.execute("SELECT COUNT(*) FROM submissions WHERE task = ?", (active_task,))
        total_submissions = cursor.fetchone()[0]  # Get the count
        
        connection.close()

        content = f"__Task {active_task} submissions__:\n(Total submissions: {total_submissions})\n\n"

        # Add many lines depending on the number of submissions
        try:
            for submission in submissions:
                content += f"{get_display_name(submission[2])} : {submission[3]} | Fetched time: ||{float_to_readable(submission[4])}||\n"

            await ctx.reply(content=content)

        except TypeError: # can happen if get_display_name throws an error; an id is not found in user.db
            # Happens, for example, if an admin /submit for someone who is not in the user.db
            await ctx.send("Someone's submission could not be retrieved.")

async def setup(bot) -> None:
    await bot.add_cog(Get(bot))
