import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api.db_classes import get_session, HostRole, LogChannel, SubmissionChannel, SeekingChannel, SubmitterRole, \
    TasksChannel, AnnouncementsChannel
from sqlalchemy import select, insert, update

from api.utils import set_submitter_role, set_host_role, set_logs_channel, set_seek_channel, set_tasks_channel, \
    set_announcements_channel, set_submission_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="config", aliases=['conf'], description="Set all the channel and stuff",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, host_role: discord.Role, logs_channel: discord.TextChannel,
                      submission_channel: discord.TextChannel,
                      seeking_channel: discord.TextChannel, submitter_role: discord.Role,
                      announcement_channel: discord.TextChannel, tasks_channel: discord.TextChannel,
                      comp: str = DEFAULT):
        await set_host_role(host_role.id, host_role.name, ctx.guild.id, comp)
        await set_logs_channel(logs_channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await set_submission_channel(submission_channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await set_seek_channel(seeking_channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await set_submitter_role(submitter_role.id, submitter_role.name, ctx.guild.id, comp)
        await set_tasks_channel(tasks_channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await set_announcements_channel(announcement_channel.id, ctx.guild.id, ctx.message.guild.id, comp)

        await ctx.send(
            f"The current host role has been set! {host_role.mention}\nThe log channel has been set! {logs_channel.mention}\nThe submission channel has been set! {submission_channel.mention}\nThe seek channel has been set! {seeking_channel.mention}\nThe submitter role has been set! {submitter_role.mention}\nThe tasks channel has been set! {tasks_channel.mention}\nThe announcement channel has been set! {announcement_channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Config(bot))
