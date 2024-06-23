from discord.ext import commands
from api.db_classes import Teams, get_session
from sqlalchemy import select, delete


class Dissolve(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dissolve", aliases=["disband"], description="Dissolve your team (WARNING: No confirmation)", with_app_command=True)
    async def dissolve(self, ctx):
        async with get_session() as session:
            # Check if the user is the leader of any team
            stmt = select(Teams).where(Teams.leader == ctx.author.id)
            result = await session.execute(stmt)
            team = result.scalar()

            if team:
                # Delete the team
                await session.execute(delete(Teams).where(Teams.leader == ctx.author.id))
                await session.commit()
                await ctx.send("Your team has been dissolved.")
            else:
                await ctx.send("You are not the leader of any team.")
                

async def setup(bot):
    await bot.add_cog(Dissolve(bot))