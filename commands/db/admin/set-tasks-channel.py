import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, insert, update

from api.db_classes import get_session, TasksChannel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetTaskschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-tasks-channel", aliases=['stc'],
                             description="Set the channel where tasks are posted (used for speed tasks)", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        async with get_session() as session:
            query = select(TasksChannel.channel_id).where(TasksChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(TasksChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)
            elif channel.id == result[0]:
                pass
            else:
                stmt = update(TasksChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The Tasks channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetTaskschannel(bot))
