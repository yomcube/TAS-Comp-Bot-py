import os

from discord.ext import commands
from dotenv import load_dotenv

from api.task_handling import end_task
from api.utils import has_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class End(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="end-task", description="End current task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        message = await end_task()
        await ctx.send(message)



async def setup(bot) -> None:
    await bot.add_cog(End(bot))
