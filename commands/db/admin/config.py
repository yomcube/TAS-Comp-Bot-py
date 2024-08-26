import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from api.db_classes import get_session, HostRole, LogChannel, SubmissionChannel, SeekingChannel, SubmitterRole
from sqlalchemy import select, insert, update

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Config(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="config", aliases=['conf'], description="Set all the channel and stuff",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, set_host_role: discord.Role, set_logs_channel: discord.TextChannel, set_submission_channel: discord.TextChannel, set_seeking_channel: discord.TextChannel, set_submitter_role: discord.Role, comp: str = DEFAULT):

        ### HOST ROLE ###
        async with get_session() as session:
            host_role = (await session.scalars(select(HostRole.comp).where(HostRole.comp == comp))).first()
            name = set_host_role.name
            role_id = set_host_role.id

            # Check if host_role doesn't exist yet for the comp
            if host_role is None:
                stmt = (insert(HostRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
                await session.execute(stmt)
            else:

                stmt = (update(HostRole).values(role_id=role_id, name=name).where(HostRole.comp == comp))
                await session.execute(stmt)

            await session.commit()
            

        ### LOGS CHANNEL ###
        async with get_session() as session:
            query = select(LogChannel.channel_id).where(LogChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=set_logs_channel.id,
                                                 comp=comp)
                await session.execute(stmt)
            elif set_logs_channel.id == result[0]:
                pass
            else:
                stmt = update(LogChannel).values(guild_id=ctx.message.guild.id, channel_id=set_logs_channel.id,
                                                 comp=comp)
                await session.execute(stmt)

            await session.commit()
            

        ### SUBMISSION CHANNEL ###
        async with get_session() as session:
            query = select(SubmissionChannel.channel_id).where(SubmissionChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(SubmissionChannel).values(guild_id=ctx.message.guild.id,
                                                        channel_id=set_submission_channel.id, comp=comp)
                await session.execute(stmt)
            elif set_submission_channel.id == result[0]:
                pass
            else:
                stmt = update(SubmissionChannel).values(guild_id=ctx.message.guild.id,
                                                        channel_id=set_submission_channel.id, comp=comp)
                await session.execute(stmt)

            await session.commit()
            

        ### SEEK CHANNEL ###
        async with get_session() as session:
            query = select(SeekingChannel.channel_id).where(SeekingChannel.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result is None:
                stmt = insert(SeekingChannel).values(guild_id=ctx.message.guild.id, channel_id=set_seeking_channel.id,
                                                     comp=comp)
                await session.execute(stmt)
            elif set_seeking_channel.id == result[0]:
                pass
            else:
                stmt = update(SeekingChannel).values(guild_id=ctx.message.guild.id, channel_id=set_seeking_channel.id,
                                                     comp=comp)
                await session.execute(stmt)

            await session.commit()
            
            
        ### SUBMITTER ROLE ###
        async with get_session() as session:
            submitter_role = (await session.scalars(select(SubmitterRole.comp).where(SubmitterRole.comp == comp))).first()
            name = set_submitter_role.name
            role_id = set_submitter_role.id

            # Check if submitter_role doesn't exist yet for the comp
            if submitter_role is None:
                stmt = (insert(SubmitterRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
                await session.execute(stmt)
            else:

                stmt = (update(SubmitterRole).values(role_id=role_id, name=name).where(SubmitterRole.comp == comp))
                await session.execute(stmt)

            await session.commit()



        await ctx.send(
            f"The current host role has been set! {set_host_role.mention}\nThe log channel has been set! {set_logs_channel.mention}\nThe submission channel has been set! {set_submission_channel.mention}\nThe seek channel has been set! {set_seeking_channel.mention}\nThe submitter role has been set! {set_submitter_role.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Config(bot))