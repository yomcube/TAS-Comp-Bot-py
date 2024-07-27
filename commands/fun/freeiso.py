from discord.ext import commands

class Iso(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="freeiso")
    async def command(self, ctx):
        await ctx.send("[FREE ISO 100% TRUE!!!](https://www.youtube.com/watch?v=HmZm8vNHBSU)")


async def setup(bot) -> None:
    await bot.add_cog(Iso(bot))