from discord.ext import commands
import discord
import sqlite3
from utils import is_task_currently_running, get_lap_time, readable_to_float, has_host_role
from api.submissions import first_time_submission


class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='submit', description='Submit', with_app_command=True)
    @has_host_role()
    async def submit(self, ctx, user: discord.Member, file: discord.Attachment):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        if not user:
            user = ctx.author

        current_task = is_task_currently_running()
        url = file.url
        id = user.id

        # retrieving lap time, to estimate submission time
        rkg_data = await file.read()

        try:
            rkg = bytearray(rkg_data)
            if rkg[:4] == b'RKGD':
                lap_times = get_lap_time(rkg)

                # float time to upload to db
                time = readable_to_float(lap_times[
                                             0])  # For most (but not all) mkw single-track tasks, the first lap time is usually the time of the submission, given the task is on lap 1 and not backwards.
            else:
                time = 0
                await ctx.reply("Invalid RKG file format")
                return

        except UnboundLocalError:
            # This exception catches blank rkg files
            time = 0
            await ctx.reply("Nice blank rkg there")
            return

        if first_time_submission(id):

            cursor.execute(
                "INSERT INTO submissions (task, name, id, url, time, dq, dq_reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (current_task[0], user.name, id, url, time, 0, '')
            )
            connection.commit()
            connection.close()

        else:
            cursor.execute("UPDATE submissions SET url=?, time=? WHERE id=?", (url, time, id))
            connection.commit()
            connection.close()

        await ctx.reply(f"A submission has been added for {user.name}!")


async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))