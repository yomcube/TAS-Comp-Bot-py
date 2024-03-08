from discord.ext import commands
import uuid
from dotenv import load_dotenv
import os


load_dotenv()
download_dir = os.getenv('DOWNLOAD_DIR')


def download_attachments(attachments) -> str:
    new_uuid = str(uuid.uuid4())
    for attachment in attachments:
        attachment.save(fp=f"{download_dir}/{new_uuid}")
    return new_uuid


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
