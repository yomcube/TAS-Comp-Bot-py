import random
from json import loads

from discord.ext import commands
import requests

class TomCube(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="tomcubesupersecretcommand", aliases=['tomcubecmd'])
    async def command(self, ctx):
        # GitHub API endpoint
        url = "https://api.github.com/users/yomcube/starred"

        # Send a request to the URL
        response = requests.get(url, timeout=60)

        # Extract valid image URLs
        starred = loads(response.text)

        if starred:
            # Select a random repository
            random_repo = random.choice(starred)

            # Send the random repository
            await ctx.send(random_repo['html_url'])
        else:
            await ctx.send("No repositories found.")

async def setup(bot) -> None:
    await bot.add_cog(TomCube(bot))
