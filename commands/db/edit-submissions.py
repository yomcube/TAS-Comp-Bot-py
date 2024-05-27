import discord
from discord.ext import commands
import sqlite3
from utils import float_to_readable


class Edit(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="edit-submissions", description="Edit submissions", with_app_command=True)
    async def command(self, ctx, user: discord.Member, time: float, dq: bool, dq_reason: str = ''):
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

        readable_time = float_to_readable(time)

        server_text = f"Succesfully edited {user}'s submission with:\nTime: from {data[4]} to {time}\nDQ: from {data_dq} to {dq}"
        dm_text = f"Your submission has been edited:\nTime: from {float_to_readable(data[4])} to {readable_time}\nDQ: from {data_dq} to {dq}"
        
        if dq == True:
            server_text += f" ({dq_reason})"
            dm_text += f" ({dq_reason})"

        # Update submission
        cursor.execute("UPDATE submissions SET time = ?, dq = ?, dq_reason = ? WHERE id = ?", (time, dq, dq_reason, user.id))
        connection.commit()
        connection.close()
        await ctx.reply(server_text)
        channel = await user.create_dm()
        await channel.send(dm_text)


async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))