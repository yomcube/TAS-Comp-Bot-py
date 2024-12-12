from discord.ext import commands
from api.db_classes import Userbase, get_session
from api.submissions import get_logs_channel
from sqlalchemy import select, update
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class RequestName(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="request-name", description="Request a set name (basically the old $setname)",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, *, new_name):

        channel = self.bot.get_channel(await get_logs_channel(DEFAULT))
        if channel:
            await channel.send("Message from ")


async def setup(bot) -> None:
    await bot.add_cog(RequestName(bot))