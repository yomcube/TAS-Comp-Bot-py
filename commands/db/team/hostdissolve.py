from discord.ext import commands

from api.task_handling import dissolve_team
from api.utils import has_host_role


class HostDissolve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hostdissolve", aliases=["hostdisband"],
                             description="Forcefully disband a team (WARNING: No confirmation)", with_app_command=True)
    @has_host_role()
    async def hostdissolve(self, ctx, index: int):
        await dissolve_team(index)
        await ctx.send("The team has been deleted.")


async def setup(bot):
    await bot.add_cog(HostDissolve(bot))
