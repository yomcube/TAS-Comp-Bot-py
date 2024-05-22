import discord
from discord.ext import commands
from api import submissions

class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Handle DMs
        # Maybe there's a better way to handle this
        if isinstance(message.channel, discord.DMChannel):
            await self.bot.process_commands(message)
            await submissions.handle_submissions(message)
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send("Succesfully saved file!")
            
            
async def setup(bot):
    await bot.add_cog(Message(bot))
