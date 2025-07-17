import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.submissions import post_submission_list, \
    submit_file
from api.utils import has_host_role, get_submission_channel, get_display_name
from discord_ext.discord_utils import edit_submission_list

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='submit', description='Submit', with_app_command=True)
    @has_host_role()
    async def submit(self, ctx, user: discord.Member, file: discord.Attachment):
        if not user:
            user = ctx.author
        url = file.url

        # retrieving lap time, to estimate submission time
        rkg_data = await file.read()

        if await submit_file(rkg_data, url, user.id, user.name, user.display_name):
            # If the submission list is already generated (most cases)
            try:
                await edit_submission_list(self)

            # First submission of the task
            except UnboundLocalError:
                submission_channel = self.bot.get_channel(await get_submission_channel(DEFAULT))
                display_name = await get_display_name(user.id)

                await post_submission_list(submission_channel, user.id, display_name)

            await ctx.reply(f"A submission has been added for {user.name}!")


async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))
