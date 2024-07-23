import discord
from discord.ext import commands
import time

class Ping(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Pong!", with_app_command=True)
    async def command(self, ctx):
        bot_latency = round(self.bot.latency * 1000, 2)
        
        start_time = time.time()
        message = await ctx.reply("Pinging...")
        end_time = time.time()
        api_latency = round((end_time - start_time) * 1000, 2)

        embed = discord.Embed(title="🏓 Pong!")
        embed.add_field(name="Bot latency", value=f"{bot_latency}ms", inline=False)
        embed.add_field(name="API latency", value=f"{api_latency}ms", inline=False)

        await message.edit(content=None, embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Ping(bot))