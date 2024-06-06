from discord.ext import commands
from api.utils import download_attachments
from api.utils import get_file_types


class Encode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="encode")
    async def encode(self, ctx, *args):
        attachments = ctx.message.attachments
        file_dict = get_file_types(attachments)

        if len(file_dict) == 2:
            filename = download_attachments(attachments)
            await ctx.send("downloaded attachment")

    @encode.error
    async def encode_error(self, ctx, error):
        await ctx.send(ctx.channel.id)


async def setup(bot):
    await bot.add_cog(Encode(bot))
