import os

from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, insert, update

from api.db_classes import get_session, SpeedTaskLength
from api.task_handling import set_speed_task_length
from api.utils import has_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Speedtasklength(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-length", aliases=['stt'],
                             description="Set the time users have to submit to speed tasks (in hours)",
                             with_app_command=True)
    @has_host_role()
    async def command(self, ctx, time: float, comp: str = DEFAULT):
        await set_speed_task_length(time, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The speed task time has been set to **{time}** hours! ")


async def setup(bot) -> None:
    await bot.add_cog(Speedtasklength(bot))
