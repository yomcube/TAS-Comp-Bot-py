from utils import download_attachments
import discord
import sqlite3

def get_submission_channel(comp):
    connection = sqlite3.connect("database/settings.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submission_channel WHERE comp = ?", (comp,))
    result = cursor.fetchone()

    channel_id = result[1]
    return channel_id

def first_time_submission(id):
    """Check if a certain user id has submitted to this competition already"""
    connection = sqlite3.connect("database/tasks.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM submissions WHERE id = ?", (id,))
    result = cursor.fetchone()
    return not result

def new_competitor(id):
    """Checks if a competitor has EVER submitted (present and past tasks)."""
    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    connection.close()
    return not result

def getDisplayname(id):
    """Returns the display name of a certain user ID."""
    connection = sqlite3.connect("database/users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM userbase WHERE id = ?", (id,))
    result = cursor.fetchone()
    connection.close()
    return result[2]

def count_submissions():
    """Counts the number of submissions in the current task."""
    connection = sqlite3.connect("database/tasks.db")
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
     #   file_name = f"Task{num}-{year}By{author_dn}"
    #    await download_attachments(attachments, file_name)
    #elif file == "rksys":
    #    file_name = f"Task{num}-{year}By{author_dn}_rksys"
    #    await download_attachments(attachments, file_name)

    author = message.author
    author_name = message.author.name
    author_id = message.author.id
    author_dn = message.author.display_name

    # Checking if submitter has ever participated before
    if new_competitor(author_id):
        # adding him to the user database.
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO userbase (user, id, display_name) VALUES (?, ?, ?)",
                       (author_name, author_id, author_dn))
        connection.commit()
        connection.close()

    # Adding submitter to the list
    submission_channel = get_submission_channel("mkw")
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
        # Try to find an editable message by the bot
        if last_message.author == self.bot.user:
            # Fetch the user data to check for display name update
            connection = sqlite3.connect("database/users.db")
            cursor = connection.cursor()
            cursor.execute("SELECT display_name, needs_update FROM userbase WHERE id = ?", (author_id,))
            user_data = cursor.fetchone()
            connection.close()


            if user_data:
                new_display_name, needs_update = user_data

                # Update the submission message if the display name has changed
                if needs_update == 1:
                    # Update the message content with the new display name
                    #TODO: FIX, doesn't work for now. doesn't edit message
                    content_lines = last_message.content.split('\n')
                    updated_content_lines = []
                    for line in content_lines:
                        if str(author_id) in line:
                            updated_content_lines.append(line.replace(getDisplayname(author_id), new_display_name))
                        else:
                            updated_content_lines.append(line)

                    new_content = '\n'.join(updated_content_lines)
                    await last_message.edit(content=new_content)

                    # Reset the needs_update flag
                    connection = sqlite3.connect("database/users.db")
                    cursor = connection.cursor()
                    cursor.execute("UPDATE userbase SET needs_update = 0 WHERE id = ?", (author_id,))
                    connection.commit()
                    connection.close()

            # Add a new line only if it's a new user ID submitting
            if first_time_submission(author_id):
                new_content = f"{last_message.content}\n{count_submissions()}. {new_display_name}"
                await last_message.edit(content=new_content)
        else:
            # If the last message is not sent by the bot, send a new one
            await channel.send(f"**__Current Submissions:__**\n1. {getDisplayname(author_id)}")
    else:
        # There are no submissions (brand-new task); send a message on the first submission
        await channel.send(f"**__Current Submissions:__**\n1. {getDisplayname(author_id)}")



async def handle_dms(message, self):
    # Handle DMs
    # Maybe there's a better way to handle this
    
    author = message.author
    author_name = message.author.name
    author_id = message.author.id
    author_dn = message.author.display_name

    if isinstance(message.channel, discord.DMChannel) and author != self.bot.user:
        #await self.bot.process_commands(message) --> for some reason, this proccessed the command twice (the bot would dm me twice in DMs).


        # this logs messages to a channel -> my private server for testing purposes
        channel = self.bot.get_channel(1239709261634732103)
        attachments = message.attachments
        if len(attachments) > 0:
            filename = attachments[0].filename
            url = attachments[0].url
        if channel:
            await channel.send("Message from " + str(author_dn) + ": " + message.content + " "
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
                if first_time_submission(author_id):
                    cursor.execute(
                        f"INSERT INTO submissions VALUES ({current_task[0]}, '{author_name}', {author_id}, '{url}', 0, 0)")
                    connection.commit()
                    connection.close()

                # If not first submission: replace old submission
                else:
                    cursor.execute("UPDATE submissions SET url=? WHERE id=?", (url, author_id))
                    connection.commit()
                    connection.close()

                # Tell the user the submission has been received
                print(f"File received!\nBy: {author}\nMessage sent: {message.content}")
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
                if first_time_submission(author_id):
                    cursor.execute(
                        f"INSERT INTO submissions VALUES ({current_task[0]}, '{author_name}', {author_id}, '{url}', 0, 0)")
                    connection.commit()
                    connection.close()

                # If not first submission: replace old submission
                else:
                    cursor.execute("UPDATE submissions SET url=? WHERE id=?", (url, author_id))
                    connection.commit()
                    connection.close()

                # Tell the user the submission has been received
                print(f"File received!\nBy: {author}\nMessage sent: {message.content}")
                await message.channel.send(
                    "`rksys.dat` detected!\nThe file was successfully saved. Type `/info` for more information about the file.")


            else:
                await message.channel.send("There is no active task.")

            # TODO make info command be an actual info command