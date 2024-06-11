import discord
from discord.ext import commands
from discord import ButtonStyle
import random
from api.utils import get_balance, add_balance, deduct_balance

class ChallengeView(discord.ui.View):
    def __init__(self, ctx, opponent, bet_amount):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
        self.bet_amount = bet_amount
        self.response = None

    async def on_timeout(self):
        if self.response is None:
            await self.disable_btns()
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
        await interaction.response.send_message("Challenge accepted!", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Decline", style=ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged user.", ephemeral=True)
            return
        self.response = "declined"
        await interaction.response.send_message("Challenge declined!", ephemeral=True)
        self.stop()

class GameView(discord.ui.View):
    def __init__(self, ctx, opponent=None, bet_amount=5):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
        self.bet_amount = bet_amount
        self.choices = {ctx.author.id: None}
        if opponent:
            self.choices[opponent.id] = None
        self.interaction_event = False

    async def on_timeout(self):
        if not self.interaction_event:
            await self.disable_btns()
            await self.ctx.send("Time's up! No response was received from one or both players within 10 seconds.")
            self.stop()

    async def disable_btns(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
            await self.message.edit(view=self)

    async def button_callback(self, interaction: discord.Interaction, choice: str):
        if interaction.user.id not in self.choices:
            await interaction.response.send_message("You are not part of this game.", ephemeral=True)
            return

        self.choices[interaction.user.id] = choice
        self.interaction_event = True
        await interaction.response.defer()
        if all(self.choices.values()):
            await self.disable_btns()
            await self.ctx.send("Both players have made their choices. Calculating the result...")
            self.stop()
        else:
            await self.ctx.send(f"{interaction.user.mention} has made their choice. Waiting for the other player.")

    @discord.ui.button(label="🪨 Rock", style=ButtonStyle.secondary)
    async def rock_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, "rock")

    @discord.ui.button(label="📰 Paper", style=ButtonStyle.success)
    async def paper_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, "paper")

    @discord.ui.button(label="✂️ Scissors", style=ButtonStyle.danger)
    async def scissors_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, "scissors")

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rockpaperscissors", description="Play Rock Paper Scissors", aliases=["rps"], with_app_command=True)
    async def command(self, ctx, opponent: discord.Member = None, bet_amount: int = 10):

        if opponent is None:
            opponent = self.bot.user

        if opponent == self.bot.user and bet_amount != 10: # You can only play for 10 coins when vs bot
            await ctx.send("The only possible bet against the bot is 10 coins. That limit is lifted when playing against other people.")

        choices = ['rock', 'paper', 'scissors']
        username = ctx.author.name
        opponent_username = opponent.name if opponent else None

        if opponent != self.bot.user:
            if bet_amount <= 0:
                await ctx.send("Nice try! Please enter a positive bet amount.")
                return

            if get_balance(username) < bet_amount:
                await ctx.send(f"{ctx.author.mention}, you do not have enough coins to place this bet.")
                return

            if get_balance(opponent_username) < bet_amount:
                await ctx.send(f"{opponent.mention} does not have enough coins to place this bet.")
                return

            if ctx.author.id == opponent.id:
                await ctx.send("You can't play against yourself.")
                return

            challenge_view = ChallengeView(ctx, opponent, bet_amount)
            challenge_message = await ctx.send(f"{opponent.mention}, you have been challenged to a game of Rock Paper Scissors by {ctx.author.mention} with a bet of {bet_amount} coins. Do you accept?", view=challenge_view)
            challenge_view.message = challenge_message
            await challenge_view.wait()

            if challenge_view.response == "accepted":
                await challenge_message.delete()
                view = GameView(ctx, opponent, bet_amount)
                message = await ctx.send(f"{ctx.author.mention} and {opponent.mention}, choose either rock, paper, or scissors!", view=view)
                view.message = message
                await view.wait()

                user_choice = view.choices[ctx.author.id]
                opponent_choice = view.choices[opponent.id]
                if user_choice is None or opponent_choice is None:
                    return

                if (user_choice == 'rock' and opponent_choice == 'scissors') or (user_choice == 'paper' and opponent_choice == 'rock') or (user_choice == 'scissors' and opponent_choice == 'paper'):
                    add_balance(username, bet_amount)
                    deduct_balance(opponent_username, bet_amount)
                    msg = f"{ctx.author.mention} wins! Their {user_choice} beats {opponent.mention}'s {opponent_choice}.\nAdded {bet_amount} coins to {ctx.author.mention}, {get_balance(username)} left in their account.\nDeducted {bet_amount} coins from {opponent.mention}, {get_balance(opponent_username)} left in their account."
                elif (user_choice == 'rock' and opponent_choice == 'paper') or (user_choice == 'paper' and opponent_choice == 'scissors') or (user_choice == 'scissors' and opponent_choice == 'rock'):
                    deduct_balance(username, bet_amount)
                    add_balance(opponent_username, bet_amount)
                    msg = f"{opponent.mention} wins! Their {opponent_choice} beats {ctx.author.mention}'s {user_choice}.\nAdded {bet_amount} coins to {opponent.mention}, {get_balance(opponent_username)} left in their account.\nDeducted {bet_amount} coins from {ctx.author.mention}, {get_balance(username)} left in their account."
                else:
                    msg = f"It's a tie! Both players chose {user_choice}.\nNo coins added."

                await ctx.send(msg)
            elif challenge_view.response == "declined":
                await ctx.send(f"{opponent.mention} declined the challenge.")
            else:
                await ctx.send("Timeout. Challenge cancelled.")
            return

        else:
            bet_amount = 10  # Force bet amount to 10 coins when playing against the bot
            if get_balance(username) < bet_amount:
                await ctx.send(f"{ctx.author.mention}, you do not have enough coins to place this bet.")
                return

            view = GameView(ctx, bet_amount=bet_amount)
            message = await ctx.reply(f"{ctx.author.mention}, choose either rock, paper, or scissors!", view=view)
            view.message = message
            await view.wait()

            user_choice = view.choices[ctx.author.id]
            if user_choice is None:
                return

            bot_choice = random.choice(choices)

            if (user_choice == 'rock' and bot_choice == 'scissors') or (user_choice == 'paper' and bot_choice == 'rock') or (user_choice == 'scissors' and bot_choice == 'paper'):
                add_balance(username, bet_amount)
                msg = f"You win! Your {user_choice} beats Bot's {bot_choice}.\nAdded {bet_amount} coins, {get_balance(username)} left in your account."
            elif (user_choice == 'rock' and bot_choice == 'paper') or (user_choice == 'paper' and bot_choice == 'scissors') or (user_choice == 'scissors' and bot_choice == 'rock'):
                deduct_balance(username, bet_amount)
                msg = f"You lose! Bot's {bot_choice} beats your {user_choice}.\nDeducted {bet_amount} coins, {get_balance(username)} left in your account."
            else:
                msg = f"It's a tie! Both players chose {user_choice}.\nNo coins added or deducted."

            await ctx.send(msg)
            return

async def setup(bot):
    await bot.add_cog(RPS(bot))
