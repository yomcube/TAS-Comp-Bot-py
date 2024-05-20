from discord.ext import commands
class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.dm_only()
    @commands.command(name='submit', aliases=[''])


    async def submit(self, ctx, files):
        await ctx.message.channel.send("submitted!")
    # TODO use JSON file to store prefixes per guild


async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))

