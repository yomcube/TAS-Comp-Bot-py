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
            await self.ctx.send(f"{self.opponent.mention} did not respond in time. Challenge cancelled.")
            self.stop()

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


class CoinFlipView(discord.ui.View):
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

    @discord.ui.button(label="Heads", style=ButtonStyle.primary)
    async def heads_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, "heads")

    @discord.ui.button(label="Tails", style=ButtonStyle.secondary)
    async def tails_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_callback(interaction, "tails")


class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="coinflip", description="Play a game of Head or Tail", aliases=["cf"],
                             with_app_command=True)
    async def command(self, ctx, opponent: discord.Member = None, bet_amount: int = 10):

        if opponent is None:
            opponent = self.bot.user

        if opponent == self.bot.user and bet_amount != 10:  # You can only play for 10 coins when vs bot
            await ctx.send("The only possible bet against the bot is 10 coins. That limit is lifted"
                           " when playing against other people.")

        guild = ctx.message.guild.id
        username = ctx.author.name
        opponent_username = opponent.name if opponent else None

        if bet_amount <= 0:
            await ctx.send("Nice try! Please enter a positive bet amount.")
            return

        if get_balance(username, guild) < bet_amount:
            await ctx.send(f"{ctx.author.mention}, you do not have enough coins to place this bet.")
            return

        if opponent != self.bot.user:
            if get_balance(opponent_username, guild) < bet_amount:
                await ctx.send(f"{opponent.mention} does not have enough coins to place this bet.")
                return

            if ctx.author.id == opponent.id:
                await ctx.send("You can't play against yourself.")
                return

            challenge_view = ChallengeView(ctx, opponent, bet_amount)
            challenge_message = await ctx.send(
                f"{opponent.mention}, you have been challenged to a game of Head or Tail by {ctx.author.mention} with a bet of {bet_amount} coins. Do you accept?",
                view=challenge_view)
            await challenge_view.wait()

            if challenge_view.response == "accepted":
                await challenge_message.delete()
                view = CoinFlipView(ctx, opponent, bet_amount)
                message = await ctx.send(f"{ctx.author.mention} and {opponent.mention}, choose either Heads or Tails!",
                                         view=view)
                view.message = message
                await view.wait()

                user_choice = view.choices[ctx.author.id]
                opponent_choice = view.choices[opponent.id]
                if user_choice is None or opponent_choice is None:
                    return

                flip_result = random.choice(['heads', 'tails'])
                if user_choice == flip_result and opponent_choice != flip_result:
                    add_balance(username, guild, bet_amount)
                    deduct_balance(opponent_username, guild, bet_amount)
                    msg = (f"{ctx.author.mention} wins! The coin landed on {flip_result}.\n"
                           f"Added {bet_amount} coins to {ctx.author.mention}, {get_balance(username, guild)} left in their account.\n"
                           f"Deducted {bet_amount} coins from {opponent.mention}, {get_balance(opponent_username, guild)} left in their account.")
                elif opponent_choice == flip_result and user_choice != flip_result:
                    deduct_balance(username, guild, bet_amount)
                    add_balance(opponent_username, guild, bet_amount)
                    msg = (f"{opponent.mention} wins! The coin landed on {flip_result}.\n"
                           f"Added {bet_amount} coins to {opponent.mention}, {get_balance(opponent_username, guild)} left in their account.\n"
                           f"Deducted {bet_amount} coins from {ctx.author.mention}, {get_balance(username, guild)} left in their account.")
                else:
                    msg = f"It's a tie! The coin landed on {flip_result}.\nNo coins added."

                await ctx.send(msg)
            else:
                await ctx.send(f"{opponent.mention} declined the challenge.")
            return

        else: # vs bot
            view = CoinFlipView(ctx)
            message = await ctx.reply(f"{ctx.author.mention}, choose either Heads or Tails!", view=view)
            view.message = message
            await view.wait()

            user_choice = view.choices[ctx.author.id]
            if user_choice is None:
                return

            flip_result = random.choice(['heads', 'tails'])

            if user_choice == flip_result:
                add_balance(username, 10)
                msg = f"You win! The coin landed on {flip_result}.\nAdded 10 coins, {get_balance(username, guild)} left in your account."
            else:
                deduct_balance(username, 10)
                msg = f"You lose! The coin landed on {flip_result}.\nDeducted 10 coins, {get_balance(username, guild)} left in your account."

            await ctx.send(msg)
            return


async def setup(bot):
    await bot.add_cog(CoinFlip(bot))
