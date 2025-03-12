from discord.ext import commands

from commands.fun.dashsupersecretcommand import random_image_search

class Shadow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shadowsupersecretcommand", aliases=['shxdcmd'])
    async def command(self, ctx):
        await random_image_search(ctx, "human+shadow+images+")

async def setup(bot):
    await bot.add_cog(Shadow(bot))
