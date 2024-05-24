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

        # TODO: Instead of seconds, this format would be preferable: 1:23.456 instead. It allows for better reading of minutes
        cursor.execute(f"UPDATE submissions SET time = {time}, dq = {dq} WHERE id = {user.id}")
        connection.commit() 
        connection.close() 
        await ctx.reply(f"Edited {user}'s submission.")

        # TODO: Send affected competitor a message saying their time was updated, and if they DQ'ed.


async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))