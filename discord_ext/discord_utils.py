import os

import discord
from dotenv import load_dotenv

from api.errors import NoSubmissionChannelError
from api.submissions import get_submission_channel, generate_submission_list
from api.utils import get_submitter_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')
async def edit_submission_list(self):
    """ Edits the submission list in the submission channel.
            Takes bot (self) as an argument -- so that the bot may retrieve the channel & message.
        """
    message_to_edit = None
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)
    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            message_to_edit = message
    formatted_submissions = generate_submission_list()
    return await message_to_edit.edit(content=formatted_submissions)

async def remove_submitter_role(bot, guild_id: int) -> None:
    # Also clear submitter roles
    submitter_role = await get_submitter_role(DEFAULT)
    server = bot.get_guild(guild_id)
    role = server.get_role(submitter_role)

    for member in role.members:
        try:
            await member.remove_roles(role)
        except discord.Forbidden:
            print(
                f"Failed to remove role {role.name} from {member.display_name} due to insufficient permissions.")
        except discord.HTTPException as e:
            print(f"Failed to remove role {role.name} from {member.display_name} due to an error: {e}")

async def delete_previous_current_submissions(bot) -> None:
    # Delete previous "Current submissions" message in submission channel
    channel_id = await get_submission_channel(DEFAULT)
    channel = bot.get_channel(channel_id)

    try:
        async for message in channel.history(limit=5):  # Adjust limit as necessary
            if message.author == bot.user:
                await message.delete()
                break

    except AttributeError:
        raise NoSubmissionChannelError("Please set the submission channel with `/set-submission-channel`! (Ask an admin if you do not have permission)")