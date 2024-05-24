from utils import download_attachments
import discord
import sqlite3

def get_submission_channel(connection, comp):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submission_channel WHERE comp = ?", (comp,))
    result = cursor.fetchone()

    channel_id = result[1]
    return channel_id

def first_time_submission(connection, id):
    """Check if a certain user id has submitted to this competition already"""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (id,))
    result = cursor.fetchone()
    return not result

def new_competitor(connection, id):
    """Checks if a competitor has EVER submitted (present and past tasks)."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    return not result

def getDisplayname(connection, id):
    """Returns the display name of a certain user ID."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    return result[2]

def count_submissions(connection):
    """Counts the number of submissions in the current task."""
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM submissions")
    result = cursor.fetchall()
    connection.close()

    return len(result)



# old parameters: message, file, num, year
async def handle_submissions(message, self):
    #attachments = message.attachments
    # TODO: Detect which comp, to limit number of files
    #attachments = attachments[:2]
    #if file == "rkg":
     #   file_name = f"Task{num}-{year}By{message.author.display_name}"
    #    await download_attachments(attachments, file_name)
    #elif file == "rksys":
    #    file_name = f"Task{num}-{year}By{message.author.display_name}_rksys"
    #    await download_attachments(attachments, file_name)



    # Checking if submitter has ever participated before
    if new_competitor(sqlite3.connect("database/users.db"), message.author.id):
        # adding him to the user database.

        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO userbase (user, id, display_name) VALUES (?, ?, ?)", (message.author.name, message.author.id, message.author.display_name))

        connection.commit()
        connection.close()

    ####################################
    # Adding submitter to the list
    ####################################


    submission_channel = get_submission_channel(sqlite3.connect("database/settings.db"), "mkw")
    channel = self.bot.get_channel(submission_channel)


    if not channel:
        print("Could not find the channel.")
        return

    async for msg in channel.history(limit=1):
        last_message = msg
        break
    else:
        last_message = None

    if last_message:
        if last_message.author == self.bot.user:
            # If the last message is sent by the bot, edit it
            new_content = f"{last_message.content}\n{count_submissions(sqlite3.connect("database/tasks.db"))}. {getDisplayname(sqlite3.connect("database/users.db"), message.author.id)}"
            await last_message.edit(content=new_content)

        else: # there are no submission (brand-new task); send a message on first submission

            # If the last message is not sent by the bot, send a new one -- this is the case for MKWTASComp server

            await channel.send(f"**__Current Submissions:__**\n1. {getDisplayname(sqlite3.connect("database/users.db"), message.author.id)}")

    else: # blank channel
        # there are no submission (brand-new task); send a message on first submission
        await channel.send(f"**__Current Submissions:__**\n1. {getDisplayname(sqlite3.connect("database/users.db"), message.author.id)}")



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

        #########################
        # Recognizing submission
        #########################

        # recognition of rkg submission
        if attachments and filename.endswith('.rkg'):

            connection = sqlite3.connect("database/tasks.db")
            cursor = connection.cursor()


            # check if a task is running
            cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
            current_task = cursor.fetchone()

            if current_task:

                # handle submission
                await handle_submissions(message, self)

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

