import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.utils import set_logs_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Setlogschannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-logs-channel", aliases=['slc'],
                             description="Set the channel where DMs with the bot are logged", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT) -> None:

        await set_logs_channel(channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The log channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Setlogschannel(bot))
