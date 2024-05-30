from discord.ext import commands
import discord
import os
import requests
from ratelimit import limits, sleep_and_retry
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('WEATHER_API_KEY')

# 1000 calls per day (over this and it's not free)
CALLS = 1000
RATE_LIMIT = 1440

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    # Empty function just to check calls
    return

class Weather(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="weather", description="Checks the weather for a specific place", with_app_command=True)
    async def command(self, ctx, *, city: str, country: str = None):
        check_limit()
        request = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric")
        response = request.json()
        
        # Check if the response contains an error message or is missing expected keys
        if response.get('cod') != 200:
            await ctx.reply(f"Error: {response.get('message', 'Unable to retrieve weather data.')}")
            return
        
        if 'name' not in response or 'sys' not in response or 'country' not in response['sys']:
            await ctx.reply("Error: Incomplete weather data received.")
            return
        print(response)
        
        embed = discord.Embed(title=f"Weather for {response['name']}, {response['sys']['country']}", color=discord.Color.blue())
        embed.add_field(name="Temperature", value=f"{(response['main']['temp']):.1f}°C")
        embed.add_field(name="Description", value=f"{response['weather'][0]['description']}")
        embed.add_field(name="Humidity", value=f"{response['main']['humidity']}%")
        embed.add_field(name="Wind", value=f"{(response['wind']['speed'] * 3.6):.1f} km/h")
        embed.set_footer(text="Powered by OpenWeatherMap API")
        await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Weather(bot))
