import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.db_classes import get_session
from commands.db.admin.set_announcements_channel import set_announcements_channel
from commands.db.admin.set_host_role import set_host_role
from commands.db.admin.set_logs_channel import set_logs_channel
from commands.db.admin.set_seeking_channel import set_seek_channel
from commands.db.admin.set_submission_channel import set_submission_channel
from commands.db.admin.set_submitter_role import set_submitter_role
from commands.db.admin.set_tasks_channel import set_tasks_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, nsmbw, sm64


class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="config", aliases=['conf'], description="Set all the channel and stuff",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, host_role: discord.Role, logs_channel: discord.TextChannel, submission_channel: discord.TextChannel,
                      seeking_channel: discord.TextChannel, submitter_role: discord.Role,
                      announcement_channel: discord.TextChannel, tasks_channel: discord.TextChannel,
                      comp: str = DEFAULT):

        async with get_session() as session:
            await set_host_role(ctx, session, host_role, comp)
            await set_logs_channel(ctx, session, logs_channel, comp)
            await set_submission_channel(ctx, session, submission_channel, comp)
            await set_seek_channel(ctx, session, seeking_channel, comp)
            await set_submitter_role(ctx, session, submitter_role, comp)
            await set_tasks_channel(ctx, session, tasks_channel, comp)
            await set_announcements_channel(ctx, session, announcement_channel, comp)

        await ctx.send("\n".join([
            f"The current host role has been set! {host_role.mention}",
            f"The log channel has been set! {logs_channel.mention}",
            f"The submission channel has been set! {submission_channel.mention}",
            f"The seek channel has been set! {seeking_channel.mention}",
            f"The submitter role has been set! {submitter_role.mention}",
            f"The tasks channel has been set! {tasks_channel.mention}",
            f"The announcement channel has been set! {announcement_channel.mention}"
        ]))


async def setup(bot) -> None:
    await bot.add_cog(Config(bot))
