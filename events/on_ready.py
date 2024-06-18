from discord.ext import commands
import sqlite3

host_role_id = None


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot is ready!')


async def setup(bot):
    await bot.add_cog(Ready(bot))
