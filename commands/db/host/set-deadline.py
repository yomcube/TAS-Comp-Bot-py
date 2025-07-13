import os

from discord.ext import commands
from dotenv import load_dotenv

from api.task_handling import set_task_deadline
from api.utils import has_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Setdeadline(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-deadline",
                             description="Adjust or set the deadline after the task has started", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, deadline: int):

        if await set_task_deadline(deadline):
            await ctx.send(f"The deadline has been set to <t:{deadline}:F> (<t:{deadline}:R>) for the current task.")


async def setup(bot) -> None:
    await bot.add_cog(Setdeadline(bot))
