from discord.ext import commands
from utils import connect_tasks

class Connect(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="connect-tasks", description="Connect task database (only do it once)", with_app_command=True)
    async def command(self, ctx):
        connect_tasks()
        await ctx.send("Succesfully connected!")  

async def setup(bot) -> None:
    await bot.add_cog(Connect(bot))