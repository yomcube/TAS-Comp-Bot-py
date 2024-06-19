import discord
from discord.ext import commands
from api.utils import float_to_readable, download_from_url, session
from api.db_classes import Submissions
from sqlalchemy import select
from api.mkwii.mkwii_utils import get_character, get_controller_type, get_lap_time, get_track, get_vehicle


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=['status'])
    @commands.dm_only()
    async def info(self, ctx):

        # Get submission
        submission = await session.execute(select(Submissions.task, Submissions.url, Submissions.time, Submissions.dq,
                                            Submissions.dq_reason).where(Submissions.user_id == ctx.author.id)).fetchone()

        if not submission:
            await ctx.reply("Either there is no ongoing task, or you have not submitted.")
            return

        # variables for all the columns
        task_num = submission[0]
        url = submission[1]
        rkg = await download_from_url(url)
        time = float_to_readable(submission[2])
        track = get_track(rkg)
        character = get_character(rkg)
        vehicle = get_vehicle(rkg)
        controller = get_controller_type(rkg)
        dq = bool(submission[3])
        dq_reason = submission[4]

        embed = discord.Embed(title=f"Task {task_num} submission", color=discord.Color.from_rgb(0, 235, 0))

        embed.add_field(name="File", value=f"{url}", inline=True)
        embed.add_field(name="Time", value=f"{time}", inline=True)
        embed.add_field(name="Track", value=f"{track}", inline=True)
        embed.add_field(name="Character", value=f"{character}", inline=True)
        embed.add_field(name="Vehicle", value=f"{vehicle}", inline=True)
        embed.add_field(name="Controller", value=f"{controller}", inline=True)
        embed.add_field(name="DQ", value=f"{dq}", inline=True)
        if dq:
            embed.add_field(name="DQ reason", value=dq_reason, inline=True)

        await ctx.reply(embed=embed)
        await ctx.send(
            "Note that unless your submission has been edited manually by a host, the time shown is the fetched lap 1 "
            "time from your rkg. It may be invalid depending on what the task is.")


async def setup(bot):
    await bot.add_cog(Info(bot))
