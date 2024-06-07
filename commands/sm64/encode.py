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
import humanize
from api.utils import download_attachment
from api.utils import get_file_types
from datetime import datetime,timezone,timedelta

DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')

ENC_SM64_DIR = os.getenv("ENC_SM64_DIR")
ENC_SM64_SCRIPTS = os.getenv("ENC_SM64_SCRIPTS")
ENC_MAX_QUEUE = int(os.getenv("ENC_MAX_QUEUE"))

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
        
        await ctx.reply(content="Your encode of {} has begun.".format(entry.filename))
    
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
        proc = await asyncio.create_subprocess_exec(*args)
        await proc.wait()
        
        # Sometimes avi files get created, but have only the header due to a crash on the first frame
        # We also check for that here
        if not os.path.isfile(avi_path) or os.path.getsize(avi_path) < 32:
            await ctx.reply("Failed to encode {}.".format(entry.filename))
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
        proc = await asyncio.create_subprocess_exec(*ffmpeg_args)
        await proc.wait()
      
        if proc.returncode != 0 or not os.path.isfile(mp4_path):
            await ctx.reply("Failed to transcode {}.".format(entry.filename))
            return
            
        await ctx.reply(file=discord.File(mp4_path), content="Your encode of {} is ready!".format(entry.filename))
        
    
    # Sends the current encoding queue into the chat
    async def send_queue(self, ctx):
        str = f"The encoding queue currently contains {len(encode_queue)} movie(s).\n\n"
        for i, entry in enumerate(encode_queue):
            str += f"#{i + 1} - {entry.filename}, {humanize.naturaldelta(float((datetime.now(timezone.utc) - entry.timestamp).seconds))}\n"
        await ctx.reply(content=str)
        
        
    @commands.command(name="encode", description = "Encodes a movie and an optional savestate into a video file")
    async def encode(self, ctx, *args):
        
        # $encode queue shows the current queue
        if len(args) > 0 and args[0].lower() == "queue".lower():
            await self.send_queue(ctx)
            return
        
        if len(encode_queue) >= ENC_MAX_QUEUE:
            await ctx.reply(content="The encode queue is currently full. Please try again later.".format(len(encode_queue), ENC_MAX_QUEUE))
            return

        attachments = ctx.message.attachments
        file_dict = get_file_types(attachments)
        
        if file_dict.get("m64") is None:
            await ctx.reply("Please provide a movie to encode.")
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
        
        await ctx.reply(content="Your encode of {} has been added to the queue at position {}.".format(filename, len(encode_queue)))

        def pop_queue(_):
            print("Finished processing frontmost entry")
            encode_queue.pop(0)
        
        asyncio.create_task(self.process_queue_front(ctx, entry)).add_done_callback(pop_queue)
        


    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
