from discord.ext import commands

class Status(commands.Cog):
    def __init(self, bot):
        self.bot = bot

    @commands.command(name="status", aliases=[])
    @commands.dm_only()
    async def status(self, ctx):
        ctx.message.channel.send("Status on submission:")
        # TODO: handle submission checking


async def setup(bot):
    bot.add_cog(Status(bot))

