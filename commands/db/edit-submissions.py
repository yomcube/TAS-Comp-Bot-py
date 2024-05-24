import discord
from discord.ext import commands
import sqlite3


class Edit(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="edit-submissions", description="Edit submissions", with_app_command=True)
    async def command(self, ctx, user: discord.Member, time: float, dq: bool):
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        
        # Find data to edit
        cursor.execute("SELECT * FROM submissions WHERE id = ?", (user.id,))
        data = cursor.fetchone()
        if not data:
            await ctx.reply(f"{user} has no submissions")
            return
        
        if data[5] == 0:
            data_dq = False
        elif data[5] == 1:
            data_dq = True

        # Update submission
        cursor.execute("UPDATE submissions SET time = ?, dq = ? WHERE id = ?", (time, dq, user.id))
        connection.commit()
        connection.close()
        await ctx.reply(f"Succesfully edited {user}'s submission with:\nTime: from {data[4]} to {time}\nDQ: from {data_dq} to {dq}")
        channel = await user.create_dm()
        await channel.send(f"Your submission has been edited:\nTime: from {data[4]} to {time}\nDQ: from {data_dq} to {dq}")


async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))