from discord.ext import commands
import sqlite3
from utils import float_to_readable, has_host_role
from api.submissions import get_display_name

class Results(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-results", description="Get the ordered results", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        
        # Get current task
        cursor.execute("SELECT * FROM submissions LIMIT 1")
        result = cursor.fetchone()
        active_task = result[0]
        
        # Get all submissions ordered by time
        cursor.execute("SELECT * FROM submissions WHERE task = ? AND dq = 0 ORDER BY time ASC", (active_task,))
        submissions = cursor.fetchall()

        # Get all DQs ordered by time
        cursor.execute("SELECT * FROM submissions WHERE task = ? AND dq = 1 ORDER BY time ASC", (active_task,))
        DQs = cursor.fetchall()


        connection.close()
        
        content = f"**__Task {active_task} Results__**:\n\n"

        try:
            # Rank valid submissions in order
            for (n, submission) in enumerate(submissions, start=1):
                display_name = get_display_name(submission[2])
                readable_time = float_to_readable(submission[4])
                content += f'{n}. {display_name} — {readable_time}\n'

            # add return incase of DQs.
            content += '\n'


            # Rank DQs in order
            for run in DQs:
                display_name = get_display_name(run[2])
                readable_time = float_to_readable(run[4])
                dq_reason = run[6]
                content += f'DQ. {display_name} — {readable_time} [{dq_reason}]\n'

            await ctx.send(content)

        except TypeError: # can happen if get_display_name throws an error; an id is not found in user.db
            # Happens, for example, if an admin /submit for someone who is not in the user.db
            await ctx.send("Someone's result could not be retrieved.")



async def setup(bot) -> None:
    await bot.add_cog(Results(bot))
