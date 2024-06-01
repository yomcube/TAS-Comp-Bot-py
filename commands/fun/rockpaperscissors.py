import discord
from discord.ext import commands
from discord import ButtonStyle
import random

class View(discord.ui.View):
    def __init__(self, msg):
        super().__init__(timeout = 10)
        self.msg = msg

    choice: str = None
    
    async def on_timeout(self):
        await self.disable_btns()
        await self.message.channel.send("No interaction was received in 10 seconds.")
        
    async def disable_btns(self):
        for item in self.children:
            item.disabled = True
        await self.msg.edit(view=self)
    
    @discord.ui.button(label="🪨", style=ButtonStyle.primary)
    async def rock_callback(self, interaction: discord.Interaction):
        self.choice = "Rock"
        await interaction.response.send_message(self.msg)
        
    @discord.ui.button(label="📰", style=ButtonStyle.primary)
    async def paper_callback(self, interaction: discord.Interaction):
        self.choice  = "Paper"
        await interaction.response.send_message(self.msg)
        
    @discord.ui.button(label="✂️", style=ButtonStyle.primary)
    async def scissors_callback(self, interaction: discord.Interaction):
        self.choice = "Scissors"
        await interaction.response.send_message(self.msg)

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rockpaperscissors", description="Play Rock Paper Scissors", aliases=["rps"], with_app_command=True)
    async def command(self, ctx, opponent: discord.Member=None):
        list = ['rock', 'paper', 'scissors']
        if not opponent:
            user_choice = View.choice
            bot_choice = random.choice(list)
            winMsg = f"You win! Your {user_choice} beats Bot {bot_choice}."
            loseMsg = f"You lose! Bot {bot_choice} beats your {user_choice}."
            if (user_choice == 'rock' and bot_choice == 'scissors') or (user_choice == 'paper' and bot_choice == 'rock') or (user_choice == 'scissors' and bot_choice == 'paper'):
                msg = winMsg
            elif (user_choice == 'rock' and bot_choice == 'paper') or (user_choice == 'paper' and bot_choice == 'scissors') or (user_choice == 'scissors' and bot_choice == 'rock'):
                msg = loseMsg
            else:
                msg = f"It's a tie! You both chose {user_choice}"
                
            view = View(msg)
            message = await ctx.send(f"{ctx.author.mention} Choose either rock, paper, or scissors with the buttons under!", view=view)
            view.message = message
            return
        if ctx.author.id == opponent.id:
            await ctx.send("You can't play against yourself.")
            return
        self.game_channel = ctx.channel
        self.players = {'X': ctx.author, 'O': opponent}

async def setup(bot):
    await bot.add_cog(RPS(bot))