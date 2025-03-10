import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, insert, update

from api.db_classes import get_session, SubmissionChannel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Setsubmissionchannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-submission-channel", aliases=['ssc'],
                             description="Set the public submission display channel", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):

        # TODO: detect which server you are in, so the comp argument is no longer needed
        async with get_session() as session:
            query = select(SubmissionChannel.channel_id).where(SubmissionChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()
            if result is None:
                stmt = insert(SubmissionChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)
            elif channel.id == result[0]:
                pass
            else:
                stmt = update(SubmissionChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The public submission display channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Setsubmissionchannel(bot))
