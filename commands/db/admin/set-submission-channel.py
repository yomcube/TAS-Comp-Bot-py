import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.submissions import set_submission_channel

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64



class Setsubmissionchannel(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-submission-channel", aliases=['ssc'],
                             description="Set the public submission display channel", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, comp: str = DEFAULT):
        await set_submission_channel(channel.id, ctx.guild.id, ctx.message.guild.id, comp)
        await ctx.send(f"The public submission display channel has been set! {channel.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Setsubmissionchannel(bot))
