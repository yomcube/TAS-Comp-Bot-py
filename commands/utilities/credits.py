from discord.ext import commands

class Credits(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="credits", description="View the authors of this bot", with_app_command=True)
    async def command(self, ctx):
        c ="""**TASCompBot** is a multi TAS-Comp bot, that will be supporting both MKW, SM64 and NSMBW TAS Comp, and maybe even more in the future.\n
This bot is in continuous development, and as such, the credits may be expanded over time.
Here is the list of contributors to this project, in alphabetical order:

  **Aurumaker72** -- SM64 encoding of .m64 files to mp4
  **Crackhex** -- Overall bot structure, and SM64 specific features
  **DashQC** -- Competition structure, MKW submission handling, host/admin commands, misc & fun commands
  **Epik95** -- Foundation of the bot
  **shxd** -- Competition structure, MKW submission handling, economy, helped with commands
  **slither** -- SM64 features, and helping with some of the fun commands
  **TomCube** -- NSMBW submission handling
  
  You can check the public GitHub repo [here](https://github.com/crackhex/TAS-Comp-Bot-py).
  If you find any bugs, please [open an issue](https://github.com/crackhex/TAS-Comp-Bot-py/issues/new).
"""

        await ctx.reply(c)


async def setup(bot) -> None:
    await bot.add_cog(Credits(bot))
