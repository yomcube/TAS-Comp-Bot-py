import sqlite3
import discord
from discord.ext import commands

def rename_in_submission_list(old_display_name, new_display_name):
    pass


class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list",
                             with_app_command=True)
    async def command(self, ctx, new_name):
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()

        try:
            # retrieve old name
            cursor.execute("SELECT from userbase WHERE id = ?", (ctx.author.id))
            result = cursor.fetchone()
            old_display_name = result[2]

            # try to update
            cursor.execute("UPDATE userbase SET display_name = ? WHERE id = ?", (new_name, ctx.author.id))

            # if the user doesn't exist in database, add him to database by encouraging to submit
            if cursor.rowcount == 0:  # Check if no rows were affected by the update
                await ctx.send("Please submit, and retry again!")

            else: # if name is found in the userbase
                connection.commit()
                await ctx.send(f"Name successfully set to {new_name}.")
                print("test")

        except sqlite3.OperationalError:
            await ctx.send("Error occured. Maybe try submitting, then retrying?")
        finally:
            connection.close()


async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))