from datetime import datetime, timedelta

import discord
from discord.ext import commands

class GiveQM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_used = {}  # Dictionary to keep track of the last usage time per user

    @commands.hybrid_command(name="giveqm", description="Give QM to another user", aliases=["gqm"], with_app_command=True)
    async def command(self, ctx, user: discord.Member):
        if user is None:
            await ctx.reply("Please mention a user")
            return

        # Get the current time
        now = datetime.utcnow()

        # Check if the user has used the command in the last 24 hours
        last_used_time = self.last_used.get(ctx.author.id)
        if last_used_time and now - last_used_time < timedelta(days=1):
            await ctx.reply("You can give QM only once a day.")
            return

        # Update the last used time
        self.last_used[ctx.author.id] = now

        await ctx.reply(f"Gave {user.mention} good QM!")

async def setup(bot):
    await bot.add_cog(GiveQM(bot))
