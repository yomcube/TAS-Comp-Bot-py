import os

from discord.ext import commands
from discord.ext.commands import Greedy
from dotenv import load_dotenv

from api.utils import has_host_role, set_speed_task_reminders

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64



class Speedtaskreminder(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-reminders", aliases=['str'],
                             description="Set the reminders necessary for speed tasks", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, reminders: Greedy[int]):
        if len(reminders) > 4:
            await ctx.send("You can't set more than 4 reminders.")
            return
        await set_speed_task_reminders(reminders, ctx.guild.id, DEFAULT)

        # Confirmation message
        await ctx.send(
            f"Reminders set: {', '.join(str(r) for r in reminders if r is not None)} minutes before the deadline.")


async def setup(bot) -> None:
    await bot.add_cog(Speedtaskreminder(bot))
