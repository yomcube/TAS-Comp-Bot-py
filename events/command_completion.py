from discord.ext import commands

class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        # TODO Handle command logs
        print(f"'{ctx.command}' command was successfully executed in '{ctx.guild}' by '{ctx.author}'.")

async def setup(bot):
    await bot.add_cog(Command(bot))
