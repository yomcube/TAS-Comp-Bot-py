import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api.db_classes import get_session, LogChannel
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
        async with get_session() as session:
            query = select(LogChannel.channel_id).where(LogChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)
            elif channel.id == result[0]:
                pass
            else:
                stmt = update(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The log channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Setlogschannel(bot))
