import discord
from discord.ext import commands
import sqlite3

class Sethostrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-host-role", aliases=['shr'], description="Set the current host role", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role):
        connection = sqlite3.connect("database/settings.db")
        cursor = connection.cursor()
        
        name = role.name
        id = role.id

        try:
            # Check if existing role already (there should only be 0 or 1)
            cursor.execute("SELECT * FROM host_role")
            existing = cursor.fetchone()

            if existing:
                cursor.execute('UPDATE host_role SET name = ?,id = ? ', (name, id,))
            else:
                cursor.execute('INSERT INTO host_role (name, id) VALUES (?, ?)', (name, id,))

            # Commit whatever change
            connection.commit()
            connection.close()

            await ctx.send(f"The current host role has been set! {role.mention}")

        except sqlite3.OperationalError as e:
            print(e)
            await ctx.send("An error occured.")

async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))