import random
from json import loads

from discord.ext import commands
import requests

class TomCube(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="tomcubesupersecretcommand", aliases=['tomcubecmd'])
    async def tomcube(self, ctx):
        # GitHub API endpoint
        url = "https://api.github.com/users/yomcube/repos"

        # Send a request to the URL with headers
        response = requests.get(url, timeout=60)

        # Extract valid image URLs
        repos = loads(response.text)

        if repos:
            # Select a random repository
            random_repo = random.choice(repos)

            # Send the random repository
            await ctx.send(random_repo['html_url'])
        else:
            await ctx.send("No repositories found.")

async def setup(bot) -> None:
    await bot.add_cog(TomCube(bot))
