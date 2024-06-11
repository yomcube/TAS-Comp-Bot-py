import discord
from discord.ext import commands
from api.utils import float_to_readable, session
from api.db_classes import Submissions
from sqlalchemy import select


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=['status'])
    @commands.dm_only()
    async def info(self, ctx):

        # Get submissions from current task
        submission = session.execute(select(Submissions.task, Submissions.url, Submissions.time, Submissions.dq,
                                            Submissions.dq_reason).where(Submissions.user_id == ctx.author.id)).fetchall()

        if not submission:
            await ctx.reply("Either there is no ongoing task, or you have not submitted.")
            return

        # variables for all the columns
        task_num = submission.task
        url = submission.url
        time = float_to_readable(submission.time)
        dq = bool(submission.dq)
        dq_reason = submission.dq_reason

        embed = discord.Embed(title=f"Task {task_num} submission", color=discord.Color.from_rgb(0, 235, 0))

        embed.add_field(name="File", value=f"{url}", inline=True)
        embed.add_field(name="Time", value=f"{time}", inline=True)
        embed.add_field(name="DQ", value=f"{dq}", inline=True)
        if dq:
            embed.add_field(name="DQ reason", value=dq_reason, inline=True)

        await ctx.reply(embed=embed)
        await ctx.send(
            "Note that unless your submission has been edited manually by a host, the time shown is the fetched lap 1 "
            "time from your rkg. It may be invalid depending on what the task is.")


async def setup(bot):
    await bot.add_cog(Info(bot))
