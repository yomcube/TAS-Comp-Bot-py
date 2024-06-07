import asyncio
from dataclasses import dataclass
import datetime
import math
import os
import subprocess
from threading import Thread
from typing import List
import uuid
import discord
from discord.ext import commands
import humanize
from api.utils import download_from_url, get_file_types
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
    
    # The async task associated with the entry
    task: asyncio.Task

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


        # Clamping: Figure out the correct ffmpeg params to fit the mp4 into 25 MB
        ffprobe_out = subprocess.check_output([
            "ffprobe",
            avi_path,
            "-v",
            "quiet",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1"
        ])
        
        length = 1000 * int(float(ffprobe_out.decode("utf-8")))
        filesize_limit = int(25e6);
        cmd = f"-i encode.avi -c:v libx264 -c:a aac -vf fps=30 "
        trate = 8 * filesize_limit / length

        if trate < 128:
            await ctx.reply("Your movie is too large.")
            return

        arate = min(16 * math.floor(trate / 128), 128)
        vrate = (trate - arate) * 0.9
        cmd += f"-maxrate ${vrate}k -bufsize ${vrate}k -b:a ${arate}k "
        cmd += f"-pix_fmt yuv420p -fs ${filesize_limit * 0.9} {mp4_path}"
        
        ffmpeg_args = [
            "ffmpeg",
            "-i",
            avi_path,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-vf",
            "fps=30",
            "-maxrate",
            f"{vrate}k",
            "-bufsize",
            f"{vrate}k",
            "-b:a",
            f"{arate}k",
            "-pix_fmt",
            "yuv420p",
            # "-fs",
            # f"{filesize_limit * 0.9}",
            f"{mp4_path}"
        ]
        
        print(cmd)
        print(ffmpeg_args)
        
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
        
    # Cancels the frontmost encode task
    async def cancel_encode(self, ctx):
        if len(encode_queue) == 0:
            await ctx.reply("The queue is empty.")
            return

        encode_queue[0].task.cancel()
        await ctx.reply("Cancelled the current encode.")
        
    @commands.command(name="encode", description = "Encodes a movie and an optional savestate into a video file")
    async def encode(self, ctx, *args):
        
        # $encode queue shows the current queue
        if len(args) > 0 and args[0].lower() == "queue".lower():
            await self.send_queue(ctx)
            return
        
        if len(args) > 0 and args[0].lower() == "cancel".lower():
            await self.cancel_encode(ctx)
            return
        
        if len(encode_queue) >= ENC_MAX_QUEUE:
            await ctx.reply(content="The encode queue is currently full. Please try again later.".format(len(encode_queue), ENC_MAX_QUEUE))
            return

        attachments = ctx.message.attachments
        
        movie_path = None
        st_path = None
        
        if len(args) > 0:
            # Pull the urls from args
            movie_path = await download_from_url(args[0])
            if len(args) > 1:
                st_path = await download_from_url(args[1])
        else:
            # Pull the urls from attachments
            file_dict = get_file_types(attachments)
            
            if file_dict.get("m64") is None:
                await ctx.reply("Please provide a movie to encode.")
                return
    
            movie_path = await download_from_url(attachments[file_dict.get("m64")].url)
            
            if file_dict.get("st") is not None:
                st_path = await download_from_url(attachments[file_dict.get("st")].url)
    
            if file_dict.get("savestate") is not None:
                st_path = await download_from_url(attachments[file_dict.get("savestate")].url)
    
        if movie_path is None:
            await ctx.reply("Failed to download the resources.")
            return
        
        # Stem of movie is also the stem of avi file
        filename = os.path.split(movie_path)[1].rpartition(".")[0]

        # When an st is provided, its stem must match the movie's stem
        if st_path is not None:
            st_stem = os.path.split(st_path)[1].rpartition(".")[0]
            if st_stem != filename:
                await ctx.reply("The provided savestate doesn't have the same name as the movie.")
                return
            
        entry = QueueEntry(uuid.uuid4(), filename, ctx.message.author, datetime.now(timezone.utc), None)
        encode_queue.append(entry)
        
        await ctx.reply(content="Your encode of {} has been added to the queue at position {}.".format(filename, len(encode_queue)))

        def pop_queue(_):
            print("Finished processing frontmost entry")
            encode_queue.pop(0)
        
        entry.task = asyncio.create_task(self.process_queue_front(ctx, entry))
        entry.task.add_done_callback(pop_queue)


    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
