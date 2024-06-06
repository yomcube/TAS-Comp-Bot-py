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
        if file_dict.get("m64") is not None:
            print(file_dict.get("m64"))
            await ctx.send("downloading m64...")
            await download_attachments(attachments, *file_dict)

    @encode.error
    async def encode_error(self, ctx, error):
        await ctx.send(ctx.channel.id)


async def setup(bot):
    await bot.add_cog(Encode(bot))
