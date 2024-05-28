import discord
from discord.ext import commands
import sqlite3
from api.submissions import float_to_readable

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=['status'])
    @commands.dm_only()
    async def info(self, ctx):
        user_id = ctx.author.id
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Get submissions from current task
        cursor.execute("SELECT * FROM submissions WHERE id= ?", (user_id,))
        submission = cursor.fetchone()  # Fetch all rows
        connection.close()

        if not submission:
            await ctx.reply("Either there is no ongoing task, or you have not submitted.")
            return


        # variables for all of the columns
        task_num = submission[0]
        url = submission[3]
        time = float_to_readable(submission[4])
        dq = bool(submission[5])
        dq_reason = submission[6]


        embed = discord.Embed(title=f"Task {task_num} submission", color=discord.Color.from_rgb(0,235,0))

        embed.add_field(name="File", value=f"{url}", inline=True)
        embed.add_field(name="Time", value=f"{time}", inline=True)
        embed.add_field(name="DQ", value=f"{dq}", inline=True)
        if dq:
            embed.add_field(name="DQ reason", value=dq_reason, inline=True)


        await ctx.reply(embed=embed)
        await ctx.send("Note that unless your submission has been edited manually by a host, the time shown is the fetched lap 1 time from your rkg. It may be invalid depending on what the task is.")




async def setup(bot):
    await bot.add_cog(Info(bot))

