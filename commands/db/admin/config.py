import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, insert, update

from api.db_classes import get_session, HostRole, LogChannel, SubmissionChannel, SeekingChannel, SubmitterRole, TasksChannel, AnnouncementsChannel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, nsmbw, sm64

### HOST ROLE ###
async def set_host_role(ctx, session, role, comp):
    host_role = (await session.scalars(select(HostRole.comp).where(HostRole.comp == comp))).first()
    name = role.name
    role_id = role.id

    # Check if host_role doesn't exist yet for the comp
    if host_role is None:
        stmt = (insert(HostRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
        await session.execute(stmt)
    else:

        stmt = (update(HostRole).values(role_id=role_id, name=name).where(HostRole.comp == comp))
        await session.execute(stmt)

    await session.commit()

### LOGS CHANNEL ###
async def set_logs_channel(ctx, session, channel, comp):
    query = select(LogChannel.channel_id).where(LogChannel.guild_id == ctx.guild.id)
    result = (await session.execute(query)).first()

    if result is None:
        stmt = insert(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id,
                                            comp=comp)
        await session.execute(stmt)
    elif channel.id == result[0]:
        pass
    else:
        stmt = update(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id,
                                            comp=comp)
        await session.execute(stmt)

    await session.commit()

### SUBMISSION CHANNEL ###
async def set_submission_channel(ctx, session, channel, comp):
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

### SEEK CHANNEL ###
async def set_seek_channel(ctx, session, channel, comp):
    query = select(SeekingChannel.channel_id).where(SeekingChannel.guild_id == ctx.guild.id)
    result = (await session.execute(query)).first()

    if result is None:
        stmt = insert(SeekingChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
        await session.execute(stmt)
    elif channel.id == result[0]:
        pass
    else:
        stmt = update(SeekingChannel).values(guild_id=ctx.message.guild.id, channel_id=channel.id, comp=comp)
        await session.execute(stmt)

    await session.commit()


### CONFIG COMMAND ###
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
            ### HOST ROLE ###
            await set_host_role(ctx, session, host_role, comp)
            ### LOGS CHANNEL ###
            await set_logs_channel(ctx, session, logs_channel, comp)
            ### SUBMISSION CHANNEL ###
            await set_submission_channel(ctx, session, submission_channel, comp)
            ### SEEK CHANNEL ###
            await set_seek_channel(ctx, session, seeking_channel, comp)


        ### SUBMITTER ROLE ###
        async with get_session() as session:
            submitter_role = (await session.scalars(select(SubmitterRole.comp).where(SubmitterRole.comp == comp))).first()
            name = submitter_role.name
            role_id = submitter_role.id

            # Check if submitter_role doesn't exist yet for the comp
            if submitter_role is None:
                stmt = (insert(SubmitterRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
                await session.execute(stmt)
            else:

                stmt = (update(SubmitterRole).values(role_id=role_id, name=name).where(SubmitterRole.comp == comp))
                await session.execute(stmt)

            await session.commit()

        ### Tasks CHANNEL ###
        async with get_session() as session:
            query = select(TasksChannel.channel_id).where(TasksChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(TasksChannel).values(guild_id=ctx.message.guild.id,
                                                     channel_id=tasks_channel.id,
                                                     comp=comp)
                await session.execute(stmt)
            elif tasks_channel.id == result[0]:
                pass
            else:
                stmt = update(TasksChannel).values(guild_id=ctx.message.guild.id,
                                                     channel_id=tasks_channel.id,
                                                     comp=comp)
                await session.execute(stmt)

            await session.commit()

            ### Announcements CHANNEL ###
            async with get_session() as session:
                query = select(AnnouncementsChannel.channel_id).where(AnnouncementsChannel.guild_id == ctx.guild.id)
                result = (await session.execute(query)).first()

                if result is None:
                    stmt = insert(AnnouncementsChannel).values(guild_id=ctx.message.guild.id,
                                                       channel_id=announcement_channel.id,
                                                       comp=comp)
                    await session.execute(stmt)
                elif announcement_channel.id == result[0]:
                    pass
                else:
                    stmt = update(AnnouncementsChannel).values(guild_id=ctx.message.guild.id,
                                                       channel_id=announcement_channel.id,
                                                       comp=comp)
                    await session.execute(stmt)

                await session.commit()






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
