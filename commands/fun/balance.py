import time

from discord.ext import commands
import discord
from api.utils import get_balance


class Balance(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="balance", description="Check your balance.", with_app_command=True)

    async def balance(self, ctx, user: discord.Member=None):
        print(time.perf_counter())
        if user:
            # TODO: probably search by ID
            user_handle = user.id
            balance = get_balance(user_handle)
            await ctx.reply(f"{user.display_name} current balance is {balance} coins.")
        else:
            user_id = ctx.author.id
            balance = get_balance(user_id)
            await ctx.reply(f"Your current balance is {balance} coins.")
        print(time.perf_counter())

async def setup(bot) -> None:
    await bot.add_cog(Balance(bot))