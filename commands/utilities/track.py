from discord.ext import commands
from api.mkwii.mkwii_utils import tracks, tracks_abbreviated
import random


class Tracks(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="tracks", description="Picks a random track from the game", with_app_command=True)
    async def command(self, ctx, abbreviated: bool = False):
        generateRandom = random.choice(tracks if not abbreviated else tracks_abbreviated)
        await ctx.reply(f'Your random track is **{generateRandom}**!')


async def setup(bot) -> None:
    await bot.add_cog(Tracks(bot))