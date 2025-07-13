import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.utils import set_seek_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetSeekchannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-seeking-channel", aliases=['sspc'],
                             description="Set the channel where team message is gonna send", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        await set_seek_channel(channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The seek channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetSeekchannel(bot))
