import sqlite3

import discord
from discord.ext import commands

class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list", with_app_command=True)
    async def command(self, ctx, name):
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()
        try:
            cursor.execute("UPDATE userbase SET display_name = ? WHERE id=?", (name, ctx.author.id))
            if cursor.rowcount == 0:  # Check if no rows were affected by the update
                await ctx.send("Please submit, and retry again!")
            else:
                connection.commit()
                connection.close()
                await ctx.send(f"Name successfully set to {name}. Check submission list!")

        except sqlite3.OperationalError:
            await ctx.send("Please submit, and retry again!")


async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))