import discord
from discord.ext import commands
import sqlite3


class Edit(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="edit-submissions", description="Edit submissions", with_app_command=True)
    async def command(self, ctx, user: discord.Member, time: str, dq: bool):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()

        # Update submission
        cursor.execute("UPDATE submissions SET time = ?, dq = ? WHERE id = ?", (time, dq, user.id))
        connection.commit()
        connection.close()
        await ctx.reply(f"Edited {user}'s submission.")


async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))