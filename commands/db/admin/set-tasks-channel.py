import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.utils import set_tasks_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetTaskschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-tasks-channel", aliases=['stc'],
                             description="Set the channel where tasks are posted (used for speed tasks)",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        await set_tasks_channel(channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The Tasks channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetTaskschannel(bot))
