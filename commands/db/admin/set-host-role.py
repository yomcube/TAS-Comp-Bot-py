import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Sethostrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-host-role", aliases=['shr'], description="Set the current host role",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role, comp: str = DEFAULT):
        connection = sqlite3.connect("database/settings.db")
        cursor = connection.cursor()

        name = role.name
        id = role.id

        try:
            # Check if existing role already
            cursor.execute("SELECT * FROM host_role WHERE comp = ?", (comp,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute('UPDATE host_role SET name = ?,id = ? WHERE comp = ?', (name, id, comp,))
            else:
                cursor.execute('INSERT INTO host_role (comp, name, id) VALUES (?, ?, ?)', (comp, name, id,))

            # Commit whatever change
            connection.commit()
            connection.close()

            await ctx.send(f"The current host role has been set! {role.mention}")

        except sqlite3.OperationalError as e:
            print(e)
            connection.close()
            await ctx.send("An error occured.")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
