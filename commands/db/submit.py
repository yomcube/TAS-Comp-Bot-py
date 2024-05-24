from discord.ext import commands
import discord
class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.dm_only()
    @commands.command(name='submit', aliases=[''])
    @commands.has_permissions(administrator=True)


    async def submit(self, ctx, user: discord.Member, files):
        await ctx.message.channel.send("submitted!")
    # TODO use JSON file to store prefixes per guild


async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))

