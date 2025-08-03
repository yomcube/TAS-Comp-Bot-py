from discord.ext import commands

from api.submissions import get_results
from api.utils import has_host_role


class Results(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-results", description="Get the ordered results", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):

        content = get_results()
        await ctx.send(content)

        # except TypeError: # can happen if get_display_name throws an error; an id is not found in user.db
        # Happens, for example, if an admin /submit for someone who is not in the user.db
        # await ctx.send("Someone's result could not be retrieved.")


async def setup(bot) -> None:
    await bot.add_cog(Results(bot))
