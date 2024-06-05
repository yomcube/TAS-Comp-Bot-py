from discord.ext import commands
from api.utils import download_attachments


class Encode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="encode")
    async def encode(self, ctx, *args, message):
        attachments = ctx.message.attachments
        if len(attachments) == 2:
            filename = download_attachments(attachments)
            await ctx.send("downloaded attachment")

    @encode.error
    async def encode_error(self, ctx, error):
        await ctx.send(ctx.message.id)


async def setup(bot):
    await bot.add_cog(Encode(bot))
