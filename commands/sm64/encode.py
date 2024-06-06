import os
import subprocess
import sqlite3
import discord
from discord.ext import commands
from api.utils import download_attachment
from api.utils import get_file_types

DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

ENC_SM64_DIR = os.getenv("ENC_SM64_DIR")
ENC_SM64_SCRIPTS = os.getenv("ENC_SM64_SCRIPTS")

MUPEN_EXE = os.path.join(ENC_SM64_DIR, "mupen", "mupen64.exe")
ROM_DIR = os.path.join(ENC_SM64_DIR, "roms")
AVI_DIR = os.path.join(ENC_SM64_DIR, "avi")

class Encode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command(name="encode")
    async def encode(self, ctx, *args):
        attachments = ctx.message.attachments
        file_dict = get_file_types(attachments)
        
        if file_dict.get("m64") is None:
            await ctx.send("Please provide a movie to encode.")
            return
        
        movie_path = await download_attachment(attachments[file_dict.get("m64")])
    
        st_path = None
    
        if file_dict.get("st") is not None:
            st_path = await download_attachment(attachments[file_dict.get("st")])
            
        if file_dict.get("savestate") is not None:
            st_path = await download_attachment(attachments[file_dict.get("savestates")])

        # Stem of movie is also the stem of avi file
        filename, _ = os.path.splitext(movie_path)
    
        avi_path = os.path.join(AVI_DIR, f"{filename}.avi")

        # If there's no st, we also omit the argument
        st_args = [] if st_path is None else [ "--st", st_path]
        
        args = [ 
            MUPEN_EXE,
            "--rom",
            os.path.join(DOWNLOAD_DIR, f"{filename}.m64"),
            *st_args,
            "--avi",
            avi_path]
        
        print(args)
        subprocess.run(args)
        
        if not os.path.isfile(avi_path):
            await ctx.send("Failed to encode the movie.")
            return

        await ctx.send(file=discord.File(avi_path), content="{}, your encode is ready!".format(ctx.message.author.mention))
        

    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
