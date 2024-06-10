import discord
import sqlite3
import os
from dotenv import load_dotenv
from api.db_classes import SubmissionChannel, session
from sqlalchemy import insert, select, update
from api.utils import get_file_types

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


def get_submission_channel(comp):
    query = select(SubmissionChannel.channel_id).where(
        SubmissionChannel.comp == comp)
    channel = session.execute(query).first()
    if channel is None:
        print(f"No submission channel found for competition '{comp}'.")
        return None

    '''connection = sqlite3.connect("database/settings.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submission_channel WHERE comp = ?", (comp,))  # there should only be 1 entry per table per competition
    result = cursor.fetchone()

    if result is not None:  # Check if result is not None before accessing index
        channel_id = result[1]
        connection.close()
        return channel_id
    else:
        # Handle case where no rows are found in the database
        connection.close()
        print(f"No submission channel found for competition '{comp}'.")
        return None'''
    return channel

def get_logs_channel(comp):
    connection = sqlite3.connect("database/settings.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM logs_channel WHERE comp = ?",
                   (comp,))  # there should only be 1 entry per table per competition
    result = cursor.fetchone()

    if result is not None:  # Check if result is not None before accessing index
        channel_id = result[1]
        connection.close()
        return channel_id
    else:
        # Handle case where no rows are found in the database
        connection.close()
        print(f"No logs channel found for competition '{comp}'.")
        return None


def first_time_submission(id):
    """Check if a certain user id has submitted to this competition already"""
    connection = sqlite3.connect("database/tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (id,))
    result = cursor.fetchone()
    return not result


def new_competitor(id):
    """Checks if a competitor has EVER submitted (present and past tasks)."""
    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    connection.close()
    return not result


def get_display_name(id):
    """Returns the display name of a certain user ID."""
    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    connection.close()
    return result[2]


def count_submissions():
    """Counts the number of submissions in the current task."""
    connection = sqlite3.connect("database/tasks.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM submissions")
    result = cursor.fetchall()
    connection.close()

    return len(result)


# old parameters: message, file, num, year
async def handle_submissions(message, self):
    author = message.author
    author_name = message.author.name
    author_id = message.author.id
    author_dn = message.author.display_name

    # Checking if submitter has ever participated before
    if new_competitor(author_id):
        # adding him to the user database.
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO userbase (user, id, display_name) VALUES (?, ?, ?)",
                       (author_name, author_id, author_dn))
        connection.commit()
        connection.close()

    ##################################################
    # Adding submission to submission list channel
    ##################################################
    submission_channel = get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    if not channel:
        print("Could not find the channel.")
        return

    async for msg in channel.history(limit=1):
        last_message = msg
        break
    else:
        last_message = None

    if last_message:
        # Try to find an editable message by the bot
        if last_message.author == self.bot.user:

            # Add a new line only if it's a new user ID submitting
            if first_time_submission(author_id):
                new_content = f"{last_message.content}\n{count_submissions()}. {get_display_name(author_id)} ||{author.mention}||"
                await last_message.edit(content=new_content)
        else:
            # If the last message is not sent by the bot, send a new one
            await channel.send(f"**__Current Submissions:__**\n1. {get_display_name(author_id)} ||{author.mention}||")
    else:
        # There are no submissions (brand-new task); send a message on the first submission -> this is for blank
        # channels
        await channel.send(f"**__Current Submissions:__**\n1. {get_display_name(author_id)} ||{author.mention}||")


async def handle_dms(message, self):
    author = message.author
    author_dn = message.author.display_name

    if isinstance(message.channel, discord.DMChannel) and author != self.bot.user:

        # log all DMs to a set channel
        channel = self.bot.get_channel(get_logs_channel(DEFAULT))
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
