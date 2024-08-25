from discord.ext import commands
import discord

class Bug(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="bug-report", description="report a bug to the devs.", with_app_command=True)
    async def command(self, ctx, *, bug: str):
        try:
            dash = self.bot.get_user(222853720692490240)
            shxd = self.bot.get_user(812615237168660481)
        
            #await dash.send(bug)
            await shxd.send(bug)

            await ctx.reply(f"Bug sent to {shxd.display_name} and {dash.display_name}, thank you!\nRemember that you can also [open an issue](https://github.com/crackhex/TAS-Comp-Bot-py/issues/new) on Github if you have an account.")
        except discord.HTTPException:
            await ctx.send("Failed to send message")


async def setup(bot) -> None:
    await bot.add_cog(Bug(bot))