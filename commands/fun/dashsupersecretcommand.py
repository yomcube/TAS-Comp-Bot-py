import random

from bs4 import BeautifulSoup
from discord.ext import commands
import requests

class Yoshi(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="dashsupersecretcommand", aliases=['dashcmd'])
    async def yoshi(self, ctx):
        # Google Image Search URL for Yoshi
        url = "https://www.google.com/search?tbm=isch&q=yoshi"

        # Headers to mimic a real browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        # Send a request to the URL with headers
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

            # Send the random Yoshi image
            await ctx.send(random_image)
        else:
            await ctx.send("No images found.")

async def setup(bot) -> None:
    await bot.add_cog(Yoshi(bot))
