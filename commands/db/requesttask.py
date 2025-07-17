import os

import discord
import shared
from discord.ext import commands
from dotenv import load_dotenv

from api.task_handling import request_task

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Requesttask(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="requesttask")
    async def requesttask(self, ctx):
        author_id = ctx.author.id
        guild_id = shared.main_guild.id
        task_number, task_year, task_desc, end_time = await request_task(author_id, guild_id)

        try:
            await ctx.author.send(
                f"You have requested the task!\n\n**__Task {task_number}, {task_year}:__** \n\n{task_desc}\n\n"
                f"You have until <t:{end_time}:f> (<t:{end_time}:R>) to submit.\nGood luck!")

        except discord.Forbidden:  # Catch DM closed error
            return await ctx.send("I couldn't send you a DM. Do you have DMs disabled?")


async def setup(bot) -> None:
    await bot.add_cog(Requesttask(bot))
