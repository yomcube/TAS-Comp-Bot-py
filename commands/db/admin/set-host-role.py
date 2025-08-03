import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.utils import set_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Sethostrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-host-role", aliases=['shr'], description="Set the current host role",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role, comp: str = DEFAULT):
        await set_host_role(role.id, role.name, ctx.guild.id, comp)
        await ctx.send(f"The current host role has been set! {role.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
