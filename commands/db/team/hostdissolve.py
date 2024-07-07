from discord.ext import commands
from api.db_classes import Teams, get_session
from api.utils import has_host_role
from sqlalchemy import select, delete



class HostDissolve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hostdissolve", aliases=["hostdisband"],
                             description="Forcefully disband a team (WARNING: No confirmation)", with_app_command=True)
    @has_host_role()
    async def hostdissolve(self, ctx, index: int):
        async with get_session() as session:
            teamlist = (await session.scalars(select(Teams))).fetchall()
            total_teams = len(teamlist)

            if index < 0 or index > total_teams:
                return await ctx.send("Invalid team number entered. See $teams")


            await session.execute(delete(Teams).where(Teams.index == index))
            await session.commit()
            await ctx.send("The team has been deleted.")


async def setup(bot):
    await bot.add_cog(HostDissolve(bot))