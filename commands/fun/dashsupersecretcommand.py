from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random



class Yoshi(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="dashsupersecretcommand")
    async def yoshi(self, ctx):
        # Yahoo Image Search URL for Yoshi
        url = "https://images.search.yahoo.com/search/images;_ylt=AwrJ7FSz9vhmV3EA.QBz6Qt.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p=yoshi&fr=yfp-t-s&imgty=photo&fr2=p%3As%2Cv%3Ai"

        # Send a request to the URL
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all image links
        images = soup.find_all("img")

        # Filter out images with data-src attribute
        valid_images = [img["data-src"] for img in images if "data-src" in img.attrs]

        # Select a random image link
        random_image = random.choice(valid_images)

        # Send the random Yoshi image
        await ctx.send(random_image)






async def setup(bot) -> None:
    await bot.add_cog(Yoshi(bot))

