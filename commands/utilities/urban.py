from discord.ext import commands
import discord
import requests

class Urban(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="urban", description="Checks the Urban for a specific place", with_app_command=True)
    async def command(self, ctx, *, term: str):
        query_split = term.split(' ')
        query = '%20'.join(query_split) # replace spaces with %20 so that it can be used in the URL
        def trim(str, max):
            return f"{str[:max]}..." if len(str) > max else str
        request = requests.get(f"https://api.urbandictionary.com/v0/define?term={query}")
        response = request.json()

        if not response['list']:
            await ctx.send("No definition found for the given word or expression.")
            return


        embed = discord.Embed(title=response['list'][0]['word'], color=discord.Color.blue())
        embed.add_field(name="Definition", value=trim(response['list'][0]['definition'], 1024), inline=False)
        embed.add_field(name="Example", value=trim(response['list'][0]['example'], 1024), inline=False)
        embed.add_field(name="Rating", value=f"{response['list'][0]['thumbs_up']} 👍\n{response['list'][0]['thumbs_down']} 👎", inline=False)
        embed.set_footer(text="Powered by Urban Dictionary API")
        await ctx.reply(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Urban(bot))