from discord.ext import commands
import discord
from api.utils import get_balance

class Balance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="balance", description="Check your balance.", with_app_command=True)
    async def balance(self, ctx, user: discord.Member=None):
        if user:
            # TODO: probably search by ID
            user_handle = user.name
            balance = get_balance(user_handle)
            await ctx.reply(f"{user.display_name} current balance is {balance} coins.")
        else:
            username = ctx.author.name
            balance = get_balance(username)
            await ctx.reply(f"Your current balance is {balance} coins.")


async def setup(bot) -> None:
    await bot.add_cog(Balance(bot))