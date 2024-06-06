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
            st_path = await download_attachment(attachments[file_dict.get("savestate")])

        # Stem of movie is also the stem of avi file
        filename = os.path.split(movie_path)[1].rpartition(".")[0]
        print(filename)
    
        avi_path = os.path.join(AVI_DIR, f"{filename}.avi")
        mp4_path = os.path.join(AVI_DIR, f"{filename}.mp4")

        # NOTE: Before encoding, delete the avi file if it exists.
        # If we don't we may leak data when a longer movie with the same name has been encoded previously
        if os.path.isfile(avi_path):
            os.remove(avi_path)

        # In the case of the mp4 file, it avoids an overwrite prompt from ffmpeg which blocks the command sequence
        if os.path.isfile(mp4_path):
            os.remove(mp4_path)
            
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

        # Convert avi to mp4 via ffmpeg
        ffmpeg_args = [
            "ffmpeg",
            "-i",
            avi_path,
            "-strict",
            "-2",
            "-pix_fmt",
            "yuv420p",
            mp4_path
        ]
        proc = subprocess.run(ffmpeg_args)
        
        if proc.returncode != 0 or not os.path.isfile(mp4_path):
            await ctx.send("Failed to encode the movie.")
            return
        
        await ctx.send(file=discord.File(mp4_path), content="{}, your encode is ready!".format(ctx.message.author.mention))
        

    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
