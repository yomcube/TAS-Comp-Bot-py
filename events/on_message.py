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
        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            await self.bot.process_commands(message)

            # this logs messages to a channel -> my private server for testing purposes
            channel = self.bot.get_channel(1239709261634732103)
            if channel:
                await channel.send(
                    "Message from " + str(message.author.display_name) + ": " + message.content + " ".join(
                        [attachment.url for attachment in message.attachments if message.attachments]))

            # reception of submission (rkg for now)
            if message.attachments and message.attachments[0].filename.endswith('.rkg'):
                await submissions.handle_submissions(message)
                print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                await message.channel.send("Succesfully saved file!")
            
            
async def setup(bot):
    await bot.add_cog(Message(bot))
