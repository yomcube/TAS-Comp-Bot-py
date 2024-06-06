import os

import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

class Setlogschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-logs-channel", aliases=['slc'],
                             description="Set the channel where DMs with the bot are logged", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        connection = sqlite3.connect("database/settings.db")
        cursor = connection.cursor()

        id = channel.id

        try:
            # Check if existing channel already
            cursor.execute("SELECT * FROM logs_channel WHERE comp = ?", (comp,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute('UPDATE logs_channel SET comp = ?, id = ? WHERE comp = ?', (comp, id, comp))

            else:
                cursor.execute('INSERT INTO logs_channel (comp, id) VALUES (?, ?)', (comp, id,))

            # Commit whatever change
            connection.commit()
            connection.close()

            await ctx.send(f"The logging channel has been set! {channel.mention}")

        except sqlite3.OperationalError as e:
            print(e)
            connection.close()
            await ctx.send("An error occured.")


async def setup(bot) -> None:
    await bot.add_cog(Setlogschannel(bot))