import discord
from discord.ext import commands
from api import submissions


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await submissions.handle_dms(message, self)
            
            
async def setup(bot):
    await bot.add_cog(Message(bot))
