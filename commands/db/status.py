from discord.ext import commands

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status", aliases=[])
    @commands.dm_only()
    async def status(self, ctx):
        await ctx.message.channel.send("Status on submission:")
        # TODO: handle submission checking


async def setup(bot):
    await bot.add_cog(Status(bot))

