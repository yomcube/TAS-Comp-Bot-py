from discord.ext import commands
from api.db_classes import Money, session
from sqlalchemy import select


class Balancetop(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="balancetop", aliases=["baltop"],
                             description="Shows the leaderboard of the richest users on this server.",
                             with_app_command=True)
    async def command(self, ctx):
        leaderboard = "**__Balance leaderboard__**:\n"
        query = select(Money.user_id, Money.coins).where(Money.guild == ctx.guild.id).order_by(Money.coins.desc())
        result = session.execute(query).fetchall()

        for i in range(0, len(result) if 5 >= len(result) else 5):
            name = ctx.guild.get_member(result[i].user_id).display_name
            leaderboard += f"{i+1}: {name}. {result[i].coins}\n"

        await ctx.send(leaderboard)


async def setup(bot) -> None:
    await bot.add_cog(Balancetop(bot))
