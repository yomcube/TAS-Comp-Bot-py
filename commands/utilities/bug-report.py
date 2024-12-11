from discord.ext import commands
import discord
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DEFAULT = getenv('DEFAULT')

class Bug(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="bug-report", description="report a bug to the devs.", with_app_command=True)
    async def command(self, ctx, *, bug: str):
        try:
            dash = self.bot.get_user(222853720692490240)
            shxd = self.bot.get_user(812615237168660481)
        
            await dash.send(bug)
            await shxd.send(bug)
            names = [ shxd.display_name, dash.display_name ]
            
            if DEFAULT == 'nsmbw':
                tomcube = self.bot.get_user(1096803802029510766)
                names.append(tomcube.display_name)
                await tomcube.send(bug)
            
            await ctx.reply(f"Bug sent to {' and '.join(names)}, thank you!\nRemember that you can also [open an issue](https://github.com/crackhex/TAS-Comp-Bot-py/issues/new) on Github if you have an account.")
        except discord.HTTPException:
            await ctx.send("Failed to send message")


async def setup(bot) -> None:
    await bot.add_cog(Bug(bot))