import os

from discord.ext import commands
from dotenv import load_dotenv

from api.task_handling import set_speed_task_desc
from api.utils import has_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Speedtaskdesc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-desc", aliases=['std'],
                             description="Set the description of the speed tasks", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, *, desc: str, comp: str = DEFAULT):
        await set_speed_task_desc(desc, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The speed task description has been set! \n{desc}")


async def setup(bot) -> None:
    await bot.add_cog(Speedtaskdesc(bot))
