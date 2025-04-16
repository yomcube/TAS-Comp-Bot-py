import random

import discord
from discord.ext import commands
from discord import ButtonStyle

from api.utils import get_balance, add_balance, deduct_balance


class ChallengeView(discord.ui.View):
    def __init__(self, ctx, opponent, bet_amount):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
        self.bet_amount = bet_amount
        self.response = None
        self.message = None

    async def on_timeout(self):
        if self.response is None:
            await self.ctx.send(f"{self.opponent.mention} did not respond in time. Challenge cancelled.")
            self.stop()

    async def disable_btns(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Accept", style=ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged user.", ephemeral=True)
            return
        self.response = "accepted"
        await self.disable_btns()
        await interaction.response.send_message("Challenge accepted!", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Decline", style=ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged user.", ephemeral=True)
            return
        self.response = "declined"
        await self.disable_btns()
        await interaction.response.send_message("Challenge declined!", ephemeral=True)
        self.stop()


class GameView(discord.ui.View):
    def __init__(self, ctx, opponent: discord.Member = None, bet_amount: int = 10):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
        self.bet_amount = bet_amount
        self.choices = {ctx.author.id: None}
        if opponent:
            self.choices[opponent.id] = None
        self.interaction_event = False
        self.message = ""

    async def on_timeout(self):
        if not self.interaction_event:
            await self.disable_btns()
            await self.ctx.send("Time's up! No response was received from one or both players within 10 seconds.")
            self.stop()

    async def disable_btns(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def button_callback(self, interaction: discord.Interaction, choice: str):
        self.choices[interaction.user.id] = choice
        self.interaction_event = True
        await interaction.response.defer()
        if all(self.choices.values()):
            await self.disable_btns()
            await self.ctx.send("Both players have made their choices. Calculating the result...")
            self.stop()
        else:
            await self.ctx.send(f"{interaction.user.mention} has made their choice. Waiting for the other player.")

    async def add_button(self, label: str, style: discord.ButtonStyle, choice: str):
        @discord.ui.button(label=label, style=style)
        async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.button_callback(interaction, choice)


class ChoiceBetCommand(commands.Cog):
    def __init__(self, bot, game, choices, default_bet = 10):
        self.bot = bot
        self.game = game
        self.choices = choices
        self.default_bet = default_bet

    async def check(self, ctx,
        guild_id: int, user_id: int, opponent_id: int,
        user_bal: int, opponent_bal: int, bet_amount: int
    ) -> str | None:
        if bet_amount <= 0:
            return "Nice try! Please enter a positive bet amount."

        if user_bal < bet_amount:
            return f"{ctx.author.mention}, you do not have enough coins to place this bet."

        if opponent != self.bot.user:
            if ctx.author.id == opponent.id:
                return "You can't play against yourself."

            if opponent_bal < bet_amount:
                return f"{opponent.mention} does not have enough coins to place this bet."


    async def challenge_wait(self, ctx, opponent: discord.Member, bet_amount: int) -> bool:
        challenge_view = ChallengeView(ctx, opponent, bet_amount)
        challenge_view.message = await ctx.send(
            f"{opponent.mention}, you have been challenged to a game of {self.game} by"
            f" {ctx.author.mention} with a bet of {bet_amount} coins. Do you accept?",
            view=challenge_view)
        res = await challenge_view.wait()
        if res:
            await challenge_view.message.delete()
        return res

    async def vs_choices_wait(self, ctx, opponent: discord.Member, bet_amount: int):
        view = GameView(ctx, opponent, bet_amount)

        choices = self.choices
        choices[-1] = f"or {choices[-1]}"
        c = ', ' if len(choices) > 2 else ' '

        message = await ctx.send(
            f"{ctx.author.mention} and {opponent.mention}, choose {c.join(choices)}!", view=view
        )
        view.message = message
        await view.wait()
        return view.choices

    async def vs_result(self,
        ctx, winner: discord.Member, loser: discord.Member,
        guild_id: int, bet_amount: int, result_message: str
    ) -> None:
        msg = None
        if None in [winner, loser]:
            msg = f"It's a tie! {result_message}.\nNo coins added."
        else:
            await add_balance(winner.id, guild, bet_amount)
            await deduct_balance(loser.id, guild, bet_amount)
            msg = (
                f"{winner.mention} wins! The coin landed on {flip_result}.\n"
                f"Added {bet_amount} coins to {ctx.author.mention},"
                f" {await get_balance(winner.id, guild)} left in their account.\n"
                f"Deducted {bet_amount} coins from {opponent.mention},"
                f" {await get_balance(loser.id, guild)} left in their account."
            )
        await ctx.send(msg)


    async def bot_choices_wait(self, ctx) -> None:
        view = GameView(ctx, opponent, bet_amount)

        choices = self.choices
        choices[-1] = f"or {choices[-1]}"
        c = ', ' if len(choices) > 2 else ' '

        message = await ctx.send(f"{ctx.author.mention}, choose {c.join(choices)}!", view=view)
        view.message = message
        await view.wait()
        return view.choices

    async def bot_result(self, ctx, win: bool, guild_id: int, result_message: str) -> None:
        if win is None:
            await ctx.send(f"It's a tie! {result_message}.\nNo coins added or deducted.")
            return

        bal = add_balance if win else deduct_balance
        bal(ctx.author.id, guild_id, self.default_bet)

        msg = (
            f"You {'win' if win else 'lose' }! {result_message}.\n{'Added' if win else 'Deducted'} "
            f"{self.default_bet} coins, {await get_balance(ctx.author.id, guild)} left in your account."
        )

        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
