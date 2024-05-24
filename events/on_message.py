import discord
from discord.ext import commands
from api import submissions
import sqlite3

class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Handle DMs
        # Maybe there's a better way to handle this
        #TODO: Move this all away; it's possible to do this via removing the prefix in dms
        #TODO: submissions.py could be used for this. It's nice to have it out of on_message - Crackhex

        if isinstance(message.channel, discord.DMChannel) and message.author != self.bot.user:
            await self.bot.process_commands(message)


            #TODO: move to file for sqlite functions
            connection = sqlite3.connect("database/tasks.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
            current_task = cursor.fetchone()

            # this logs messages to a channel -> my private server for testing purposes
            channel = self.bot.get_channel(1233075197561536553)
            attachments = message.attachments
            if len(attachments) > 0:
                filename = attachments[0].filename
                url = attachments[0].url
            if channel:
                await channel.send(
                    f"Message from {message.author.display_name}:\n{message.content}".join(
                        [attachment.url for attachment in attachments if attachments]))

            # recognition of rkg submission
            if attachments and filename.endswith('.rkg'):
                if current_task:
                    await submissions.handle_submissions(message, "rkg", 1, 2024)
                    cursor.execute(f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', '{url}', 0, 0)")
                    print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                    await message.channel.send("`.rkg` file detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
                else:
                    await message.channel.send("There is no active task.")
                
                
            # recognition of rksys submission
            elif attachments and filename == 'rksys.dat':
                if current_task:
                    await submissions.handle_submissions(message, "rksys", 1, 2024)
                    cursor.execute(f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', '{url}', 0, 0)")
                    print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                    await message.channel.send("`rksys.dat` detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
                else:
                    await message.channel.send("There is no active task.")
               
                
            #TODO make info command be an actual info command
            
            
async def setup(bot):
    await bot.add_cog(Message(bot))
