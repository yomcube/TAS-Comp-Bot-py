from discord.ext import commands


class Sync(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def command(self, ctx):
        msg = await ctx.send("Syncing...")
        sync = await self.bot.tree.sync()
        await msg.edit(content=f"Synced {len(sync)} commands for {self.bot.user}!")


async def setup(bot) -> None:
    await bot.add_cog(Sync(bot))