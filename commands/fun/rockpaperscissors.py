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

    async def on_timeout(self):
        if self.response is None:
            await self.disable_btns()
            await self.ctx.send(f"{self.opponent.mention} did not respond in time. Challenge cancelled.")
            self.stop()

    async def disable_btns(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
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
        print("Timeout triggered")
        await self.disable_btns()
        await self.ctx.send("Time's up! No response was received from one or both players within 10 seconds.")
        self.stop()

    async def disable_btns(self):
        print("Disabling buttons")
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
            print("All choices made")
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

    @commands.hybrid_command(name="rockpaperscissors", description="Play Rock Paper Scissors", aliases=["rps"],
                             with_app_command=True)
    async def command(self, ctx, opponent: discord.Member = None, bet_amount: int = 10):

        if opponent is None:
            opponent = self.bot.user

        if opponent == self.bot.user and bet_amount != 10:  # You can only play for 10 coins when vs bot
            await ctx.send("The only possible bet against the bot is 10 coins. That limit is lifted"
                           " when playing against other people.")

        choices = ['rock', 'paper', 'scissors']
        user_id = ctx.author.id
        guild_id = ctx.message.guild.id
        opponent_id = opponent.id if opponent else None
        user_bal = await get_balance(user_id, guild_id)
        opponent_bal = await get_balance(opponent_id, guild_id)
        wins = [
            ('rock', 'scissors'),
            ('paper', 'rock'),
            ('scissors', 'paper')
        ]
        if opponent != self.bot.user:
            if bet_amount <= 0:
                await ctx.send("Nice try! Please enter a positive bet amount.")
                return

            if user_bal < bet_amount:
                await ctx.send(f"{ctx.author.mention}, you do not have enough coins to place this bet.")
                return

            if opponent_bal < bet_amount:
                await ctx.send(f"{opponent.mention} does not have enough coins to place this bet.")
                return

            if ctx.author.id == opponent.id:
                await ctx.send("You can't play against yourself.")
                return

            challenge_view = ChallengeView(ctx, opponent, bet_amount)
            challenge_message = await ctx.send(
                f"{opponent.mention}, you have been challenged to a game of Rock Paper Scissors "
                f"by {ctx.author.mention} with a bet of {bet_amount} coins. Do you accept?",
                view=challenge_view
            )
            await challenge_view.wait()

            if challenge_view.response == "accepted":
                await challenge_message.delete()
                view = GameView(ctx, opponent, bet_amount)
                message = await ctx.send(
                    f"{ctx.author.mention} and {opponent.mention}, choose either rock, paper, or scissors!", view=view)
                view.message = message
                await view.wait()

                user_choice = view.choices[ctx.author.id]
                opponent_choice = view.choices[opponent.id]
                if user_choice is None or opponent_choice is None:
                    return


                if user_choice == opponent_choice:
                    msg = "It's a tie! Both players chose {user_choice}.\nNo coins added."
                
                else:
                    if (user_choice, opponent_choice) in wins:
                        await add_balance(user_id, guild_id, bet_amount)
                        await deduct_balance(opponent_id, guild_id, bet_amount)
                        msg = (f"{ctx.author.mention} wins! Their {user_choice} beats their {opponent_choice}.\nAdded "
                            f"{bet_amount} coins to {ctx.author.mention}, {user_bal + bet_amount} left in their account.\n"
                            f"Deducted {bet_amount} coins from {opponent.mention}, {opponent_bal - bet_amount} left in their account."
                        )
                    else:
                        await deduct_balance(user_id, guild_id, bet_amount)
                        await add_balance(opponent_id, guild_id, bet_amount)
                        msg = (
                            f"{opponent.mention} wins! Their {opponent_choice} beats their {user_choice}.\nAdded {bet_amount} "
                            f"coins to {opponent.mention}, {opponent_bal + bet_amount} left in their account.\nDeducted "
                            f"{bet_amount} coins from {ctx.author.mention}, {user_bal - bet_amount} left in their account."
                        )
                

                await ctx.send(msg)
            else:
                await ctx.send(f"{opponent.mention} declined the challenge.")
            return


        bet_amount = 10  # Force bet amount to 10 coins when playing against the bot
        if user_bal < bet_amount:
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

        if (user_choice == opponent_choice):
            msg = f"It's a tie! Both players chose {user_choice}.\nNo coins added or deducted."
        else:
            if (user_choice, opponent_choice) in wins:
                await add_balance(user_id, guild_id, bet_amount)
                msg = (f"You win! Your {user_choice} beats Bot's {bot_choice}.\nAdded {bet_amount} coins, "
                        f"{user_bal + bet_amount} left in your account."
                )
            else:
                await deduct_balance(user_id, guild_id, bet_amount)
                msg = (f"You lose! Bot's {bot_choice} beats your {user_choice}.\nDeducted {bet_amount} coins, "
                        f"{user_bal - bet_amount} left in your account."
                )

        await ctx.send(msg)
        return


async def setup(bot):
    await bot.add_cog(RPS(bot))
