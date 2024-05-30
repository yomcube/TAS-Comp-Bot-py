import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="say", description="Say everything you say", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, channel: discord.TextChannel, *, message: str):
        # Send the message to the specified channel
        await channel.send(message)
        await ctx.reply(f"Message sent to {channel.mention}.")


async def setup(bot) -> None:
    await bot.add_cog(Say(bot))