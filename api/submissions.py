from utils import download_attachments
import discord
import sqlite3


async def handle_submissions(message, file, num, year):
    attachments = message.attachments
    # TODO: Detect which comp, to limit number of files
    attachments = attachments[:2]
    if file == "rkg":
        file_name = f"Task{num}-{year}By{message.author.display_name}"
        await download_attachments(attachments, file_name)
    elif file == "rksys":
        file_name = f"Task{num}-{year}By{message.author.display_name}_rksys"
        await download_attachments(attachments, file_name)
        
async def handle_dms(message, self):
        # Handle DMs
        # Maybe there's a better way to handle this

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
                    await handle_submissions(message, "rkg", 1, 2024)
                    cursor.execute(f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', '{url}', 0, 0)")
                    print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                    await message.channel.send("`.rkg` file detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
                else:
                    await message.channel.send("There is no active task.")
                
                
            # recognition of rksys submission
            elif attachments and filename == 'rksys.dat':
                if current_task:
                    await handle_submissions(message, "rksys", 1, 2024)
                    cursor.execute(f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', '{url}', 0, 0)")
                    print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                    await message.channel.send("`rksys.dat` detected!\nThe file was successfully saved. Type `/info` for more information about the file.")
                else:
                    await message.channel.send("There is no active task.")
               
                
            #TODO make info command be an actual info command
    

