import discord
import os
from dotenv import load_dotenv
from api.db_classes import SubmissionChannel, Userbase, get_session, Submissions, LogChannel, SeekingChannel
from sqlalchemy import insert, select
from api.utils import get_file_types, get_team_size, is_in_team

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def get_submission_channel(comp):
    async with get_session() as session:
        query = select(SubmissionChannel.channel_id).where(SubmissionChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No submission channel found for competition '{comp}'.")
            return None
        return channel[0]


async def get_submission_channel_guild(channel_id):
    async with get_session() as session:
        query = select(SubmissionChannel.guild_id).where(SubmissionChannel.channel_id == channel_id)
        guild_id = (await session.scalars(query)).first()
        if guild_id is None:
            return None
        return guild_id


async def get_logs_channel(comp):
    async with get_session() as session:
        query = select(LogChannel.channel_id).where(LogChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No logging channel found for '{comp}'.")
            return None
        return channel[0]
    
async def get_seeking_channel(comp):
    async with get_session() as session:
        query = select(SeekingChannel.channel_id).where(SeekingChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No logging channel found for '{comp}'.")
            return None
        return channel[0]


async def first_time_submission(user_id):
    """Check if a certain user id has submitted to this competition already"""
    async with get_session() as session:
        query = select(Submissions.user_id).where(Submissions.user_id == user_id)
        result = (await session.execute(query)).first()

        return not result


async def new_competitor(user_id):
    """Checks if a competitor has EVER submitted (present and past tasks)."""
    async with get_session() as session:
        query = select(Userbase.user_id).where(Userbase.user_id == user_id)
        result = (await session.execute(query)).first()
        return not result


async def get_display_name(user_id):
    """Returns the display name of a certain user ID."""
    async with get_session() as session:
        result = (await session.scalars(select(Userbase.display_name).where(Userbase.user_id == user_id))).first()
        return result


async def count_submissions():
    """Counts the number of submissions in the current task."""
    async with get_session() as session:
        query = select(Submissions)
        result = (await session.scalars(query)).fetchall()
        return len(result)


async def handle_submissions(message, self):
    author = message.author
    author_name = message.author.name
    author_id = message.author.id
    author_dn = message.author.display_name

    ##################################################
    # Adding submission to submission list channel
    ##################################################
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    # Checking if submitter has ever participated before
    if await new_competitor(author_id):
        # adding him to the user database.
        async with get_session() as session:
            await session.execute(insert(Userbase).values(user_id=author_id, user=author_name, display_name=author_dn))
            await session.commit()

    if not channel:
        print("Could not find the channel.")
        return

    async for msg in channel.history(limit=1):
        last_message = msg
        break
    else:
        last_message = None

    author_display_name = await get_display_name(author_id)

    if last_message:
        # Try to find an editable message by the bot
        if last_message.author == self.bot.user:

            # Add a new line only if it's a new user ID submitting
            if await first_time_submission(author_id):
                new_content = (f"{last_message.content}\n{await count_submissions()}. {author_display_name}"
                               f" ||{author.mention}||")
                await last_message.edit(content=new_content)
        else:
            # If the last message is not sent by the bot, send a new one
            await channel.send(
                f"**__Current Submissions:__**\n1. {author_display_name} ||{author.mention}||")
    else:
        # There are no submissions (brand-new task); send a message on the first submission -> this is for blank
        # channels
        await channel.send(
            f"**__Current Submissions:__**\n1. {author_display_name} ||{author.mention}||")


async def handle_dms(message, self):
    author = message.author
    author_dn = message.author.display_name

    if isinstance(message.channel, discord.DMChannel) and author != self.bot.user:

        # log all DMs to a set channel
        channel = self.bot.get_channel(await get_logs_channel(DEFAULT))
        attachments = message.attachments
        if channel:
            await channel.send("Message from " + str(author_dn) + ": " + message.content + " "
                               .join([attachment.url for attachment in message.attachments if message.attachments]))

        #########################
        # Recognizing submission
        #########################

        if len(attachments) > 0:
            file_dict = get_file_types(attachments)
            from api.mkwii.mkwii_file_handling import handle_mkwii_files  # TODO: use a class here?

            try:
                await handle_mkwii_files(message, attachments, file_dict, self)

            except TimeoutError:
                await channel.send("Could not process Files!")
