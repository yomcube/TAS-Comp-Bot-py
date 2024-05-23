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
            channel = self.bot.get_channel(1233075197561536553)
            if channel:
                await channel.send(
                    f"Message from {message.author.display_name}:\n{message.content}".join(
                        [attachment.url for attachment in message.attachments if message.attachments]))

            # recognition of rkg submission
            if message.attachments and message.attachments[0].filename.endswith('.rkg'):
                await submissions.handle_submissions(message, "rkg", 1, 2024)
                print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                await message.channel.send("`.rkg` file detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
            # recognition of rksys submission
            elif message.attachments and message.attachments[0].filename == 'rksys.dat':
                await submissions.handle_submissions(message, "rksys", 1, 2024)
                print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                await message.channel.send("`rksys.dat` detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
                
            #TODO make info command be an actual info command
            
            
async def setup(bot):
    await bot.add_cog(Message(bot))
