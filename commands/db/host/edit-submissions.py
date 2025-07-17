import discord
from discord.ext import commands

from api.submissions import edit_submission
from api.utils import has_host_role


class Edit(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="edit-submissions", description="Edit submissions", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, user: discord.Member, time: float, dq: bool, dq_reason: str = ''):
        server_text, dm_text = await edit_submission(user.id, str(user), time, dq, dq_reason)
        await ctx.reply(server_text,
                        allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
        channel = await user.create_dm()
        await channel.send(dm_text,
                           allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)


async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))
