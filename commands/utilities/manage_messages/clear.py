from discord.ext import commands
import discord

class Clear(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="clear", description="Clear messages", with_app_command=True)
    @commands.has_permissions(manage_messages=True)
    async def command(self, ctx: commands.Context, amount: int):
        try:
            int(amount)
        except ValueError:  # Error handler
            await ctx.send('Please enter a valid integer as amount.', delete_after=10)
        else:
            await ctx.channel.purge(limit=amount+1)
            embed = discord.Embed(title=f"Cleared {amount} messages", color=discord.Color.blue())
            message = await ctx.send(embed=embed, ephemeral=True)
            await message.delete(delay=10)  # Delete after 10 seconds

async def setup(bot) -> None:
    await bot.add_cog(Clear(bot))
