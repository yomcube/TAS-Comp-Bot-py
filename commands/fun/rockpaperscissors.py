import discord
from discord.ext import commands
from discord import ButtonStyle
import random

class ChallengeView(discord.ui.View):
    def __init__(self, ctx, opponent):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
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

class GameView(discord.ui.View):
    def __init__(self, ctx, opponent=None):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.opponent = opponent
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
    async def command(self, ctx, opponent: discord.Member = None):
        choices = ['rock', 'paper', 'scissors']

        if opponent:
            
            if ctx.author.id == opponent.id:
                await ctx.send("You can't play against yourself.")
                return

            challenge_view = ChallengeView(ctx, opponent)
            challenge_message = await ctx.send(f"{opponent.mention}, you have been challenged to a game of Rock Paper Scissors by {ctx.author.mention}. Do you accept?", view=challenge_view)
            await challenge_view.wait()

            if challenge_view.response == "accepted":
                await challenge_message.delete()
                view = GameView(ctx, opponent)
                message = await ctx.send(f"{ctx.author.mention} and {opponent.mention}, choose either rock, paper, or scissors!", view=view)
                view.message = message
                await view.wait()

                user_choice = view.choices[ctx.author.id]
                opponent_choice = view.choices[opponent.id]
                if user_choice is None or opponent_choice is None:
                    return

                winMsg = f"{ctx.author.mention} wins! Their {user_choice} beats their {opponent_choice}."
                loseMsg = f"{opponent.mention} wins! Their {opponent_choice} beats their {user_choice}."
                tieMsg = f"It's a tie! Both players chose {user_choice}."

                if (user_choice == 'rock' and opponent_choice == 'scissors') or (user_choice == 'paper' and opponent_choice == 'rock') or (user_choice == 'scissors' and opponent_choice == 'paper'):
                    msg = winMsg
                elif (user_choice == 'rock' and opponent_choice == 'paper') or (user_choice == 'paper' and opponent_choice == 'scissors') or (user_choice == 'scissors' and opponent_choice == 'rock'):
                    msg = loseMsg
                else:
                    msg = tieMsg

                await ctx.send(msg)
            else:
                await ctx.send(f"{opponent.mention} declined the challenge.")
            return

        else:
            view = GameView(ctx)
            message = await ctx.reply(f"{ctx.author.mention}, choose either rock, paper, or scissors!", view=view)
            view.message = message
            await view.wait()

            user_choice = view.choices[ctx.author.id]
            if user_choice is None:
                return

            bot_choice = random.choice(choices)
            winMsg = f"You win! Your {user_choice} beats Bot's {bot_choice}."
            loseMsg = f"You lose! Bot's {bot_choice} beats your {user_choice}."
            tieMsg = f"It's a tie! You both chose {user_choice}."

            if (user_choice == 'rock' and bot_choice == 'scissors') or (user_choice == 'paper' and bot_choice == 'rock') or (user_choice == 'scissors' and bot_choice == 'paper'):
                msg = winMsg
            elif (user_choice == 'rock' and bot_choice == 'paper') or (user_choice == 'paper' and bot_choice == 'scissors') or (user_choice == 'scissors' and bot_choice == 'rock'):
                msg = loseMsg
            else:
                msg = tieMsg

            await ctx.send(msg)
            return

async def setup(bot):
    await bot.add_cog(RPS(bot))
