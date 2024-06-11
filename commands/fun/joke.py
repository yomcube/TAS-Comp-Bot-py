from discord.ext import commands
import requests
import random
from jokeapi import Jokes

class Joke(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="joke",description="The bot will tell you a joke!",with_app_command=True)
    async def command(self, ctx):

        async def jokeapi(): # This is the first of 2 joke API used
            j = await Jokes()
            joke = await j.get_joke(blacklist=['nsfw', 'racist', 'explicit'])
            if joke["type"] == "single":  # Print the joke
                return await ctx.send(joke["joke"])
            else:
                await ctx.send(joke["setup"])
                await ctx.send(joke["delivery"])
                return

        async def official_jokes_api(): # This is the second of 2 joke API used
            response = requests.get("https://official-joke-api.appspot.com/random_joke")
            if response.status_code == 200:
                joke_data = response.json()
                return  await ctx.send(f'{joke_data.get("setup")}\n{joke_data.get("punchline")}')
            else:
                return ctx.send("Error, please retry.")


        random_api = random.choice([jokeapi, official_jokes_api])
        await random_api()


async def setup(bot) -> None:
    await bot.add_cog(Joke(bot))