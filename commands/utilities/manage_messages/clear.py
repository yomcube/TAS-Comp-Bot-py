from discord.ext import commands
import discord

class Clear(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="clear", description="Clear messages", with_app_command=True)
    @commands.has_permissions(manage_messages=True)
    async def command(self, ctx, amount: int):
        try:
            int(amount)
        except: # Error handler
            await ctx.send('Please enter a valid integer as amount.')
        else:
            await ctx.channel.purge(limit=amount+1)
        embed = discord.Embed(title=f"Cleared {amount} messages", color=discord.Color.blue())
        await ctx.send(embed=embed, ephemeral=True)


async def setup(bot) -> None:
    await bot.add_cog(Clear(bot))