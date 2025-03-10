import discord
from discord.ext import commands

from api.utils import add_balance


class Addcoins(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="addcoins", description="Add coins to user's balances (admin only)",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def addcoins(self, ctx, user: discord.Member, amount: int):
        user_id = user.id
        await add_balance(user_id, ctx.guild.id, amount)
        await ctx.reply(f"Added {amount} coins to {user.display_name}'s balance.",
            allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)


async def setup(bot) -> None:
    await bot.add_cog(Addcoins(bot))
