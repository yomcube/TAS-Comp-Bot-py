import asyncio
from dataclasses import dataclass
import datetime
import os
import subprocess
from threading import Thread
from typing import List
import uuid
import discord
from discord.ext import commands
from api.utils import download_attachment
from api.utils import get_file_types
from datetime import datetime,timezone

DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

ENC_SM64_DIR = os.getenv("ENC_SM64_DIR")
ENC_SM64_SCRIPTS = os.getenv("ENC_SM64_SCRIPTS")

MUPEN_EXE = os.path.join(ENC_SM64_DIR, "mupen", "mupen64.exe")
ROM_DIR = os.path.join(ENC_SM64_DIR, "roms")
AVI_DIR = os.path.join(ENC_SM64_DIR, "avi")

@dataclass
class QueueEntry:
    # The entry's unique identifier
    uid: uuid.UUID
    
    # The movie and savestate's filename stem.
    # Associated m64 must exist in DOWNLOAD_DIR, along with its optional savestate
    filename: str
    
    # The queue entry's author
    author: discord.User
    
    # Timestamp at which the entry has entered the queue
    timestamp: datetime

# Back-to-front vector of recent tasks
encode_queue: List[QueueEntry] = []

# Thread which is currently encoding a movie 
encode_thread = None

class Encode(commands.Cog):
     
    def __init__(self, bot) -> None:
        self.bot = bot
        
    async def process_queue_front(self, ctx, entry: QueueEntry):
        """ Processes the entry at the front of the encode queue. """
        
        # Wait until this entry reaches the front
        while encode_queue[0].uid != entry.uid:
            print(f"Waiting for {entry.filename} to reach front...")
            await asyncio.sleep(1)
        
        await ctx.send(content="{}, your encode of {} has begun.".format(ctx.message.author.mention, entry.filename))
    
        avi_path = os.path.join(AVI_DIR, f"{entry.filename}.avi")
        mp4_path = os.path.join(AVI_DIR, f"{entry.filename}.mp4")

        # NOTE: Before encoding, delete the avi file if it exists.
        # If we don't we may leak data when a longer movie with the same name has been encoded previously
        if os.path.isfile(avi_path):
            os.remove(avi_path)

        # In the case of the mp4 file, it avoids an overwrite prompt from ffmpeg which blocks the command sequence
        if os.path.isfile(mp4_path):
            os.remove(mp4_path)

        args = [ 
            MUPEN_EXE,
            "--rom",
            os.path.join(DOWNLOAD_DIR, f"{entry.filename}.m64"),
            "--avi",
            avi_path]
        
        print(args)
        proc = subprocess.run(args)
        
        if not os.path.isfile(avi_path):
            await ctx.send("Failed to encode {}.".format(entry.filename))
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
            await ctx.send("Failed to transcode {}.".format(entry.filename))
            return
        
        # Remove the entry from the queue now that it's finished
        encode_queue.pop(0)
        
        await ctx.send(file=discord.File(mp4_path), content="{}, your encode of {} is ready!".format(ctx.message.author.mention, entry.filename))
        
    @commands.command(name="encode")
    async def encode(self, ctx, *args):
        attachments = ctx.message.attachments
        file_dict = get_file_types(attachments)
        
        if file_dict.get("m64") is None:
            await ctx.send("Please provide a movie to encode.")
            return

        attachments = ctx.message.attachments
        
        movie_path = await download_attachment(attachments[file_dict.get("m64")])
        
        if file_dict.get("st") is not None:
            await download_attachment(attachments[file_dict.get("st")])
 
        if file_dict.get("savestate") is not None:
            await download_attachment(attachments[file_dict.get("savestate")])
    
        # Stem of movie is also the stem of avi file
        filename = os.path.split(movie_path)[1].rpartition(".")[0]

        entry = QueueEntry(uuid.uuid4(), filename, ctx.message.author, datetime.now(timezone.utc))
        encode_queue.append(entry)
        
        await ctx.send(content="{}, your encode of {} has been added to the queue at position {}.".format(ctx.message.author.mention, filename, len(encode_queue)))

        # FIXME: This still blocks...
        asyncio.create_task(self.process_queue_front(ctx, entry))
        

    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
