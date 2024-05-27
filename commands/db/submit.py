from discord.ext import commands
import discord
import sqlite3
from utils import is_task_currently_running, get_lap_time, readable_to_float
from api.submissions import first_time_submission


class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='submit', description='Submit', with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def submit(self, ctx, file: discord.Attachment=None, user: discord.Member=None):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        if not user:
            user = ctx.author
        
        current_task = is_task_currently_running()
        url = file.url
        id = user.id
        
        # retrieving lap time, to estimate submission time

        rkg_data = await file[0].read()

        try:
            rkg = bytearray(rkg_data)
            if rkg[:4] == b'RKGD':
                lap_times = get_lap_time(rkg)

            # float time to upload to db
            time = readable_to_float(lap_times[0]) # For most (but not all) mkw single-track tasks, the first lap time is usually the time of the submission, given the task is on lap 1 and not backwards.

        except UnboundLocalError:
            # This exception catches blank rkg files
            time = 0
            await ctx.reply("Nice blank rkg there")
                    
        if first_time_submission(id):
            # Assuming the table `submissions` has columns: task, name, id, url, time, dq, dq_reason
            cursor.execute(
                "INSERT INTO submissions (task, name, id, url, time, dq, dq_reason) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                (current_task[0], user.name, id, url, time, 0, '')
            )
            connection.commit()
            connection.close()


            # If not first submission: replace old submission
        else:
            cursor.execute("UPDATE submissions SET url=?, WHERE id=?", (url, id))
            connection.commit()
            connection.close()
            
        
        await ctx.reply("submitted!")

async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))
