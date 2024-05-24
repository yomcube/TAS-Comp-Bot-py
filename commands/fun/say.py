import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="say", description="Say everything you say", with_app_command=True)
    async def command(self, ctx, text):
        await ctx.reply(text)


async def setup(bot) -> None:
    await bot.add_cog(Say(bot))