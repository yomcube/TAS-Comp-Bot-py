from discord.ext import commands
from api.db_classes import Teams, get_session
from api.utils import is_in_team, get_team_size
from api.submissions import get_display_name
from sqlalchemy import select, delete


class TeamsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_users = {}
        self.ctx = None
        self.author = None
        self.team_size = None

    @commands.hybrid_command(name="teams", description="Shows all the teams and available players",
                             with_app_command=True)
    async def teams(self, ctx):
        self.ctx = ctx
        self.author = ctx.author
        self.team_size = await get_team_size()

        # Is there a task running?
        if self.team_size is None:
            return await ctx.send("There is no task running currently.")

        # Verify if it's indeed a collab task
        elif self.team_size < 2:
            return await ctx.send("This is a solo task. You may **not** collaborate!")

        content = "__**Confirmed teams:**__\n"

        # Retrieve teams from db
        async with get_session() as session:
            result = await session.execute(select(Teams))
            rows = result.scalars().all()

        # Write each line of content
        for row in rows:
            row_data = []
            for column in row.__table__.columns:
                value = getattr(row, column.name)
                if value is not None and column.name not in ["index", "team_name"]:
                    user = self.bot.get_user(value)
                    if user:
                        row_data.append(user.display_name)

            display_names = " & ".join(row_data)
            if row.team_name:
                content += f"{row.index}. {row.team_name} ({display_names})\n"
            else:
                content += f"{row.index}. {display_names}\n"

        return await ctx.send(content)

        return await ctx.send(content)


async def setup(bot):
    await bot.add_cog(TeamsCommand(bot))