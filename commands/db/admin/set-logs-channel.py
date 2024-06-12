import os

import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
from api.db_classes import session, LogChannel
from sqlalchemy import select, insert, update

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

class Setlogschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-logs-channel", aliases=['slc'],
                             description="Set the channel where DMs with the bot are logged", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        query = select(LogChannel.channel_id).where(LogChannel.guild_id == ctx.guild.id)
        result = session.execute(query).first()

        if result is None:
            stmt = insert(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id,comp=comp)
            session.execute(stmt)
        elif channel.id == result[0]:
            pass
        else:
            stmt = update(LogChannel).values( guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
            session.execute(stmt)

        session.commit()
        await ctx.send(f"The log channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Setlogschannel(bot))