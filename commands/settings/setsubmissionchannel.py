import discord
from discord.ext import commands
import sqlite3

class Setsubmissionchannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="setsubmissionchannel", aliases=['ssc'])
    async def setsubmissionchannel(self, ctx, comp, id):
        # TODO: detect which server you are in, so the comp argument is no longer needed

        connection = sqlite3.connect("database/settings.db")
        cursor = connection.cursor()

        try:
            # Check if existing channel already
            cursor.execute("SELECT * FROM submission_channel WHERE comp = ?", (comp,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute('UPDATE submission_channel SET comp = ?, id = ? WHERE comp = ?', (comp, id, comp))

            else:
                cursor.execute('INSERT INTO submission_channel (comp, id) VALUES (?, ?)', (comp, id,))

            # Commit whatever change
            connection.commit()
            connection.close()

            await ctx.send("The public submission display channel has been set!")

        except sqlite3.OperationalError as e:
            print(e)
            await ctx.send("An error occured.")





async def setup(bot) -> None:
    await bot.add_cog(Setsubmissionchannel(bot))