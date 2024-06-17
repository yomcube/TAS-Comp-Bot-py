from discord.ext import commands
import discord


class Clear(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Clear messages", with_app_command=True)
    @commands.has_permissions(manage_messages=True)
    async def command(self, ctx, amount: int):
        if amount < 1:
            await ctx.send('The number of messages to delete must be at least 1.', ephemeral=True)
            return

        deleting_message = await ctx.send(f'Deleting {amount} messages...', ephemeral=True)
        await deleting_message.delete()

        # Perform the purge operation
        if ctx.interaction:
            deleted = await ctx.channel.purge(limit=amount)
            confirmation_message = await ctx.send(f'Deleted {len(deleted)} messages.', ephemeral=True)
        else:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message itself
            confirmation_message = await ctx.send(f'Deleted {len(deleted) - 1} messages.', ephemeral=True)
        await confirmation_message.delete(delay=5)


async def setup(bot) -> None:
    await bot.add_cog(Clear(bot))
