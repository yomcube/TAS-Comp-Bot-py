import discord
from discord.ext import commands
from api.utils import float_to_readable, get_team_size, is_in_team, get_leader
from api.db_classes import Submissions, get_session
from sqlalchemy import select
from struct import unpack


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=['status'])
    @commands.dm_only()
    async def info(self, ctx):
        async with get_session() as session:
            # Verify if collab task, and if author is in a team
            team_size = await get_team_size()

            # TODO: Temporary fix for a bug where you can't use $info after task has ended; currently only will work for
            #  solo tasks after task has ended

            if team_size is not None and team_size > 1 and await is_in_team(ctx.author.id):
                submission_id = await get_leader(ctx.author.id)
            else:
                submission_id = ctx.author.id


            # Get submission
            submission = (await session.execute(select(Submissions.task, Submissions.url, Submissions.time,
                                                Submissions.dq, Submissions.dq_reason, Submissions.character)
                                                .where(Submissions.user_id == submission_id))).fetchone()

        if not submission:
            await ctx.reply("Either there is no ongoing task, or you have not submitted.")
            return

        # variables for all the columns
        task_num = submission[0]
        url = submission[1]
        time = submission[2]
        dq = bool(submission[3])
        dq_reason = submission[4]
        dtm = submission[5]
        
        def yesno(b):
            return "Yes" if bool(b) else "No"
        
        embed = discord.Embed(title=f"Task {task_num} submission", color=discord.Color.from_rgb(0, 235, 0))

        embed.add_field(name="File", value=url, inline=True)
        embed.add_field(name="Time", value=f"{time / 60} seconds", inline=True)
        embed.add_field(name="DQ", value=yesno(dq), inline=True)
        if dq:
            embed.add_field(name="DQ reason", value=dq_reason, inline=True)
        
        # Separator
        embed.add_field(name="", value="", inline=False)
        
        (gameId, isWii, controllers, savestate, vi, inputs, lag,
            rerecords, video, audio, md5, timestamp) = unpack("<6s3B3Q8xL32x16s16s16sq", dtm[4:0x89])
        
        embed.add_field(name="Game ID", value=gameId.decode('utf-8'), inline=True)
        embed.add_field(name="Is Wii Game", value=yesno(isWii), inline=True)
        
        controllers_str = ""
        first = True
        i = 0
        while i < 8:
            if controllers & (1 << i):
                controllers_str += ("" if first else ", ") + ("GC " if i/4 < 1 else "Wii ") + str((i % 4) + 1)
                first = False
            i += 1
        
        embed.add_field(name="Controllers Plugged", value=controllers_str, inline=True)
        embed.add_field(name="From Savestate", value=yesno(savestate), inline=True)
        embed.add_field(name="VI Count", value=vi, inline=True)
        embed.add_field(name="Input Count", value=inputs, inline=True)
        embed.add_field(name="Lag Count", value=lag, inline=True)
        embed.add_field(name="Rerecords", value=rerecords, inline=True)
        embed.add_field(name="Video Backend", value=video.decode('utf-8'), inline=True)
        embed.add_field(name="Audio Backend", value=audio.decode('utf-8'), inline=True)
        embed.add_field(name="MD5 Hash", value=f"`{md5.hex()}`", inline=False)
        embed.add_field(name="Start Time", value=f"<t:{timestamp}> (<t:{timestamp}:R>)", inline=False)


        await ctx.reply(embed=embed)
        await ctx.send(
            "Note that unless your submission has been edited manually by a host, the time shown is the "
            "VI count from your DTM.\nFull DTM file info can be found [here](https://yomcube.github.io/file-utils/?f=DTM).")


async def setup(bot):
    await bot.add_cog(Info(bot))
