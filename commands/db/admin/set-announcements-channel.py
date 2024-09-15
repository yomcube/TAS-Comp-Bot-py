import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api.db_classes import get_session, AnnouncementsChannel
from sqlalchemy import select, insert, update

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetAnnouncementschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-announcements-channel", aliases=['sac'],
                             description="Set the channel where announcements are posted (used for speed tasks)", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        async with get_session() as session:
            query = select(AnnouncementsChannel.channel_id).where(AnnouncementsChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(AnnouncementsChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)
            elif channel.id == result[0]:
                pass
            else:
                stmt = update(AnnouncementsChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The announcements channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetAnnouncementschannel(bot))
