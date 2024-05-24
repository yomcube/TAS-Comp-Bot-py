from utils import download_attachments
import discord
import sqlite3


def first_time_submission(connection, id):
    """Check if a certain user id has submitted to this competition already"""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (id,))
    result = cursor.fetchone()
    return not (result)


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
        #await self.bot.process_commands(message) --> for some reason, this proccessed the command twice (the bot would dm me twice in DMs).


        # this logs messages to a channel -> my private server for testing purposes
        channel = self.bot.get_channel(1243651327226019890)
        attachments = message.attachments
        if len(attachments) > 0:
            filename = attachments[0].filename
            url = attachments[0].url
        if channel:
            await channel.send("Message from " + str(message.author.display_name) + ": " + message.content + " "
                               .join([attachment.url for attachment in message.attachments if message.attachments]))



        # recognition of rkg submission
        if attachments and filename.endswith('.rkg'):

            connection = sqlite3.connect("database/tasks.db")
            cursor = connection.cursor()


            # check if a task is running
            cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
            current_task = cursor.fetchone()

            if current_task:

                # rename file
                await handle_submissions(message, "rkg", current_task[0], 2024)

                # Add first-time submission
                if first_time_submission(connection, message.author.id):
                    cursor.execute(
                        f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', {message.author.id}, '{url}', 0, 0)")
                    connection.commit()
                    connection.close()

                # If not first submission: replace old submission
                else:
                    cursor.execute("UPDATE submissions SET url=? WHERE id=?", (url, message.author.id))
                    connection.commit()
                    connection.close()

                # Tell the user the submission has been received
                print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                await message.channel.send(
                    "`.rkg` file detected!\nThe file was successfully saved. Type `/info` for more information about the file.")

            # No ongoing task
            else:
                await message.channel.send("There is no active task.")


        # recognition of rksys submission
        elif attachments and filename == 'rksys.dat':
            connection = sqlite3.connect("database/tasks.db")
            cursor = connection.cursor()

            # check if a task is running
            cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
            current_task = cursor.fetchone()

            if current_task:

                # rename file
                await handle_submissions(message, "rksys", current_task[0], 2024)

                # Add first-time submission
                if first_time_submission(connection, message.author.id):
                    cursor.execute(
                        f"INSERT INTO submissions VALUES ({current_task[0]}, '{message.author.name}', {message.author.id}, '{url}', 0, 0)")
                    connection.commit()
                    connection.close()

                # If not first submission: replace old submission
                else:
                    cursor.execute("UPDATE submissions SET url=? WHERE id=?", (url, message.author.id))
                    connection.commit()
                    connection.close()

                # Tell the user the submission has been received
                print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
                await message.channel.send(
                    "`rksys.dat` detected!\nThe file was successfully saved. Type `/info` for more information about the file.")


            else:
                await message.channel.send("There is no active task.")

            # TODO make info command be an actual info command

