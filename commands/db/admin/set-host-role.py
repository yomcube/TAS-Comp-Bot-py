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
        name = role.name
        role_id = role.id
        guild_id = ctx.guild.id
        await set_host_role(role_id, name, guild_id, comp)
        await ctx.send(f"The current host role has been set! {role.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
