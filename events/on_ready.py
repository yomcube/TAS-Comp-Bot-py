import discord
import shared
from discord.ext import commands
import sqlite3
from commands.db.requesttask import check_deadlines

host_role_id = None


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global detected_guild
        detected_guild = None

    @commands.Cog.listener()
    async def on_ready(self):
        shared.main_guild = self.bot.guilds[0]
        print(f"Detected main server: {shared.main_guild.name} (ID: {shared.main_guild.id})")

        check_deadlines.start(self.bot)


async def setup(bot):
    await bot.add_cog(Ready(bot))
