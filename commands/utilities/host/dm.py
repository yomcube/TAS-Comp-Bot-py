import discord
from discord.ext import commands
from api.utils import has_host_role

class DM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dm", description="Dm a user", with_app_command=True)
    @has_host_role()
    @commands.has_role("Developer")
    async def command(self, ctx, user: discord.Member, *, message):
        """Send a direct message to a user"""
        try:
            # Prepare the logged the message
            full_message = f"Message sent to {user.display_name}: {message}"

            # Send the direct message to the user
            await user.send(message)

            # Send the logged message
            await ctx.send(full_message)
        except discord.HTTPException:
            await ctx.send("Failed to send message")


async def setup(bot) -> None:
    await bot.add_cog(DM(bot))