import random

from bs4 import BeautifulSoup
from discord.ext import commands
import requests

class Shadow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shadowsupersecretcommand", aliases=['shxdcmd'])
    async def command(self, ctx):
        # Google Image Search URL for "human shadow images"
        url = "https://www.google.com/search?tbm=isch&q=human+shadow+images"

        # Send a request to the URL
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(url, headers=headers, timeout=60)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all image tags
        images = soup.find_all("img")

        # Extract valid image URLs
        valid_images = [img["src"] for img in images if "src" in img.attrs and img["src"].startswith("http")]

        if valid_images:
            # Select a random image link
            random_image = random.choice(valid_images)

            # Send the random image URL
            await ctx.send(random_image)
        else:
            await ctx.send("No images found.")

async def setup(bot):
    await bot.add_cog(Shadow(bot))
