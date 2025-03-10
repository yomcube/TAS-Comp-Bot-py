import random

from discord.ext import commands
import requests

class Quote(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @commands.command(name="quote")
    async def quote(self, ctx):
        api1 = "https://dummyjson.com/quotes/random"
        api2 = "https://quotes-api-self.vercel.app/quote"

        random_api = random.choice([api1, api2])

        request = requests.get(random_api, timeout=60)
        formatted_request = dict(request.json())

        quote = formatted_request.get('quote')
        author = formatted_request.get('author')

        message = f"> {quote}\n -{author}"

        await ctx.send(message)



async def setup(bot) -> None:
    await bot.add_cog(Quote(bot))
