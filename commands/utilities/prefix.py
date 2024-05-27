from discord.ext import commands


class Prefix(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='prefix', aliases=[''])
    async def prefix(self, ctx, new_prefix):
        print(new_prefix)
        await ctx.message.channel.send(new_prefix)
    # TODO use JSON file to store prefixes per guild
    # On second thought, we could streamline all the data with sqlite3, since that's what we are using here


async def setup(bot) -> None:
    await bot.add_cog(Prefix(bot))
