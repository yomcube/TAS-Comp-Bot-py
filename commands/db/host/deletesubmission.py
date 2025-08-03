import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.submissions import delete_submission
from api.utils import has_host_role
from discord_ext.discord_utils import edit_submission_list

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class DeleteSubmission(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="delete-submission", description="Delete someone's submission", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, user: discord.Member):
        # delete the user's submission
        await delete_submission(user.id, user.display_name)
        # Update submission list
        await edit_submission_list(self)

        await ctx.send(f"{user.display_name}'s submission has been deleted.",
                       allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)


async def setup(bot) -> None:
    await bot.add_cog(DeleteSubmission(bot))
