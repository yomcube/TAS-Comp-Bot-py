import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api.db_classes import get_session, JoinChannel
from sqlalchemy import select, insert, update

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetJoinChannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-join-channel", aliases=['sjc'],
                             description="Set the channel where the bot will react with those eyes or whatever", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        async with get_session() as session:
            query = select(JoinChannel.channel_id).where(JoinChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(JoinChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)
            elif channel.id == result[0]:
                pass
            else:
                stmt = update(JoinChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The join channel has been set! :eyes: {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetJoinChannel(bot))
