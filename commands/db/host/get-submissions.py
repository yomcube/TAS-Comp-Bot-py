import asyncio

from discord import AllowedMentions
from discord.ext import commands

from api.submissions import get_submissions
from api.utils import has_host_role
from discord_ext.discord_wrappers import command_handler

class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task",
                             with_app_command=True)
    @has_host_role()
    @command_handler()
    async def command(self, ctx):
        msg_limit = 2000
        buffer = 50  # Small buffer to prevent exceeding the limit
        submissions_parts, header = await get_submissions(msg_limit, buffer)

        # Send the messages, including the header in the first message
        for i, part in enumerate(submissions_parts):
            if i == 0:
                if len(header + part) > msg_limit:
                    await ctx.reply(header,
                        allowed_mentions=AllowedMentions.none(), suppress_embeds=True)
                    await ctx.reply(part,
                        allowed_mentions=AllowedMentions.none(), suppress_embeds=True)
                else:
                    await ctx.reply(header + part,
                        allowed_mentions=AllowedMentions.none(), suppress_embeds=True)
            else:
                await ctx.reply(part,
                    allowed_mentions=AllowedMentions.none(), suppress_embeds=True)

            await asyncio.sleep(1)


async def setup(bot) -> None:
    await bot.add_cog(Get(bot))