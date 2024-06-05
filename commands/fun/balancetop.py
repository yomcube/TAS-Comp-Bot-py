from discord.ext import commands
import sqlite3

class Balancetop(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="balancetop", aliases=["baltop"],
                             description="Shows the leaderboard of the richest users on this server.", with_app_command=True)
    async def command(self, ctx):
        connection = sqlite3.connect("./database/economy.db")
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM money ORDER BY coins DESC")

        request = cursor.fetchall()
        leaderboard = "**__Balance leaderboard__**:\n"

        for n, row in enumerate(request, start=1):
            leaderboard += f"{n}. {row[0]} — {row[1]} coins\n"

        connection.close()

        await ctx.send(leaderboard)




async def setup(bot) -> None:
    await bot.add_cog(Balancetop(bot))