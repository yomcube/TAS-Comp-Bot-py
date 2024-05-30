from discord.ext import commands

class Rig(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="rig")
    @commands.has_permissions(administrator=True)
    async def command(self, ctx):
        await ctx.send("1")


async def setup(bot) -> None:
    await bot.add_cog(Rig(bot))