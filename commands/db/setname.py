import sqlite3
from discord.ext import commands
from api.submissions import get_submission_channel
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def rename_in_submission_list(self, old_display_name, new_display_name):
    submission_channel = get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            lines = message.content.split('\n')
            new_lines = [lines[0]]  # Preserve the first line as is ("Current submissions")

            # Check if the new display name is already in use in the rest of the lines
            for line in lines[1:]:
                if new_display_name in line:
                    return

            for line in lines[1:]:
                if old_display_name in line:
                    line = line.replace(old_display_name, new_display_name)
                new_lines.append(line)

            new_content = '\n'.join(new_lines)
            if new_content != message.content:
                await message.edit(content=new_content)
            break  # Stop after finding the last bot message

class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list", with_app_command=True)
    async def command(self, ctx, *, new_name):
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()

        if '@' in new_name:
            return await ctx.reply("You may not use @ in your name.")

        if len(new_name) > 120:
            return await ctx.reply("Your name is too long!")

        try:
            # retrieve old name
            cursor.execute("SELECT * from userbase WHERE id = ?", (ctx.author.id,))
            result = cursor.fetchone()
            old_display_name = result[2]

            # Check if the new name is already in use in the database
            cursor.execute("SELECT * from userbase WHERE display_name = ?", (new_name,))
            if cursor.fetchone():
                return await ctx.reply("The name is already in use by another user.")

            # try to update
            cursor.execute("UPDATE userbase SET display_name = ? WHERE id = ?", (new_name, ctx.author.id))

            # if the user doesn't exist in database, add him to database by encouraging to submit
            if cursor.rowcount == 0:  # Check if no rows were affected by the update
                await ctx.send("Please submit, and retry again!")

            else: # if name is found in the userbase
                connection.commit()
                await ctx.send(f"Name successfully set to **{new_name}**.")

                await rename_in_submission_list(self, old_display_name, new_name)

        except (sqlite3.OperationalError, TypeError): # another way of catching error
            await ctx.send("Error occured. Maybe try submitting, then retrying?")
        finally:
            connection.close()

async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))