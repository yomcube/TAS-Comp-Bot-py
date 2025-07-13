import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.utils import set_display_name
from discord_ext.discord_utils import edit_submission_list

load_dotenv()
DEFAULT = os.getenv('DEFAULT')



class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, user: discord.Member, *, new_name: commands.clean_content):
        # TODO: Check if correct
        await set_display_name(user.id, str(new_name))
        # Update submission list
        await edit_submission_list(self)

        await ctx.send(f"Sucessfully set <@{user.id}>'s name to **{new_name}**.",
                       allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)


async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))
