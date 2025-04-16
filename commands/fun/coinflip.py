import random

import discord
from discord.ext import commands
from discord import ButtonStyle

from api.utils import get_balance, add_balance, deduct_balance
from commands.fun.choice_bet_command import ChoiceBetCommand

class CoinFlip(commands.Cog, ChoiceBetCommand):
    def __init__(
        self, bot,
        game = "Heads or Tails",
        choices = ['heads', 'tails'],
        default_bet = 10
    ):
        super().__init__(bot, game, choices, default_bet)

    @commands.hybrid_command(name="coinflip", description="Play a game of Head or Tail", aliases=["cf"],
                             with_app_command=True)
    async def command(self, ctx, opponent: discord.Member = None, bet_amount: int = 10):
        if opponent in [None, self.bot.user] and bet_amount != self.default_bet:
            opponent = self.bot.user
            await ctx.send(
                f"The only possible bet against the bot is {self.default_bet} coins."
                " That limit is lifted when playing against other people."
            )

        guild = ctx.message.guild.id

        if err := self.check(guild, ctx.author.id, opponent.id, user_bal, opponent_bal, bet_amount):
            await ctx.send(err)

        if opponent != self.bot.user:
            if await self.challenge_wait():
                choices = self.vs_choices_wait()

                user_choice = choices[ctx.author.id]
                opponent_choice = choices[opponent.id]
                if None in [user_choice, opponent_choice]:
                    return

                flip_result = random.choice(self.choices)
                win = (
                    None if user_choice == opponent_choice
                    else user_choice == flip_result != opponent_choice
                )
                winner = None if win is None else ctx.author if win else opponent
                loser = None if win is None else opponent if win else ctx.author
                vs_result(ctx, winner, loser, guild, bet_amount, f"The coin landed on {flip_result}")
            else:
                await ctx.send(f"{opponent.mention} declined the challenge.")
            return

        # vs bot
        choices = bot_choices_wait(ctx)

        user_choice = choices[user_id]
        if user_choice is None:
            return

        flip_result = random.choice(self.choices)

        await bot_result(ctx, user_choice == flip_result, guild, f"The coin landed on {flip_result}")


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
