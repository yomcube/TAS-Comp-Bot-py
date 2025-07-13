import os

from dotenv import load_dotenv

from api.submissions import get_submission_channel, generate_submission_list

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

