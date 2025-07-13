import os

from discord.ext import commands
from dotenv import load_dotenv

from api.utils import toggle_reminder_pings

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Togglereminderpings(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="toggle-reminder-pings", aliases=['trp'],
                             description="Toggle on/off everyone reminder pings in speed tasks", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, comp: str = DEFAULT):
        new_setting = await toggle_reminder_pings(ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The speed task reminders pings have been set to {new_setting}!")


async def setup(bot) -> None:
    await bot.add_cog(Togglereminderpings(bot))
