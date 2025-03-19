import discord
from discord.ext import commands

from api.utils import get_balance

class BetCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check(self, ctx, opponent: discord.Member, bet_amount: int, default_bet_amount: int):
        if opponent in [None, self.bot.user] and bet_amount != default_bet_amount:  # You can only play for 10 coins when vs bot
            opponent = self.bot.user
            bet_amount = default_bet_amount
            await ctx.send(f"The only possible bet against the bot is {default_bet_amount} coins. "
                            "That limit is lifted when playing against other people.")

        user_id = ctx.author.id
        guild_id = ctx.message.guild.id
        opponent_id = opponent.id if opponent else None
        user_bal = await get_balance(user_id, guild_id)
        opponent_bal = await get_balance(opponent_id, guild_id)

        if bet_amount <= 0:
            await ctx.send("Nice try! Please enter a positive bet amount.")
            return None

        if user_bal < bet_amount:
            await ctx.send(f"{ctx.author.mention}, you do not have enough coins to place this bet.")
            return None

        if opponent != self.bot.user:
            if bet_amount <= 0:
                await ctx.send("Nice try! Please enter a positive bet amount.")
                return None

            if opponent_bal < bet_amount:
                await ctx.send(f"{opponent.mention} does not have enough coins to place this bet.")
                return None

            if ctx.author.id == opponent.id:
                await ctx.send("You can't play against yourself.")
                return None

        return (user_id, guild_id, opponent_id, user_bal, opponent_bal, bet_amount)
