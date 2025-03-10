from discord.ext import commands
from sqlalchemy import select, delete

from api.db_classes import Teams, get_session
from api.utils import is_in_team

async def reorder_primary_keys():
    async with get_session() as session:

        # Retrieve the teams
        query = select(Teams).order_by(Teams.index)
        result = await session.execute(query)
        teams = result.scalars().all()

        # Reassign indexes
        for idx, team in enumerate(teams, start=1):
            team.index = idx

        await session.commit()

class LeaveTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="leaveteam", description="Leave your team in a collab task", with_app_command=True)
    async def command(self, ctx):

        if not await is_in_team(ctx.author.id):
            return await ctx.send("You are already not in a team!")

        async with get_session() as session:
            # Check if the user is the leader of any team
            stmt = select(Teams).where(Teams.leader == ctx.author.id)
            result = await session.execute(stmt)
            leader = result.scalar()

            if leader:
                # Delete the team
                await session.execute(delete(Teams).where(Teams.leader == ctx.author.id))

                # Rearrange team indexes
                await reorder_primary_keys()

                await session.commit()
                await ctx.send("You have abandoned your team. Your team has been dissolved")
            else:
                result = await session.execute(select(Teams))
                rows = result.scalars().all()

                for row in rows:
                    # Iterate through columns dynamically
                    for column in Teams.__mapper__.columns:
                        if isinstance(getattr(row, column.name), int) and getattr(row, column.name) == ctx.author.id:
                            # Set the value to None or blank
                            setattr(row, column.name, None)  # or use '' for a blank string

                await ctx.send("You have abandoned your team.")

                # Disband the team if 1 person remaining (it's not a team anymore)
                for row in rows:
                    if row.leader and row.user2 is None and row.user3 is None and row.user4 is None:
                        await session.delete(row)

                        # Rearrange team indexes
                        await reorder_primary_keys()

                        await ctx.send(f"<@{row.leader}> Poor you :( Your partner(s) gave up on you. Your team has been dissolved.")

                await session.commit()



async def setup(bot):
    await bot.add_cog(LeaveTeam(bot))
