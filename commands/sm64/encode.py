import asyncio
from dataclasses import dataclass
import datetime
import math
import os
from typing import List
import uuid
import discord
from discord.ext import commands
from video import FFmpegBuilder, ffprobe
import humanize
from api.utils import download_from_url, get_file_types
from datetime import datetime, timezone

DOWNLOAD_DIR = os.path.abspath(os.getenv("DOWNLOAD_DIR"))
ENC_MUPEN_DIR = os.path.abspath(os.getenv("ENC_MUPEN_DIR"))
ENC_AVI_DIR = os.path.abspath(os.getenv("ENC_AVI_DIR"))
ENC_SM64_SCRIPTS = os.path.abspath(os.getenv("ENC_SM64_SCRIPTS"))
ENC_MAX_QUEUE = int(os.getenv("ENC_MAX_QUEUE"))

MUPEN_EXE = os.path.join(ENC_MUPEN_DIR, "mupen64.exe")


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


async def cancel_encode(ctx):
    # Cancels the frontmost encode task
    # FIXME: Require role for this action
    if len(encode_queue) == 0:
        await ctx.reply("The queue is empty.")
        return

    encode_queue[0].task.cancel()
    await ctx.reply("Cancelled the current encode.")


async def send_queue(ctx):
    # Sends the current encoding queue into the chat
    str = f"The encoding queue currently contains {len(encode_queue)} movie(s).\n\n"
    for i, entry in enumerate(encode_queue):
        str += f"#{i + 1} - {entry.filename}, {humanize.naturaldelta(float((datetime.now(timezone.utc) - entry.timestamp).seconds))}\n"
    await ctx.reply(content=str)


async def process_queue_front(ctx, entry: QueueEntry):
    """ Processes the entry at the front of the encode queue. """

    # Wait until this entry reaches the front
    while encode_queue[0].uid != entry.uid:
        print(f"Waiting for {entry.filename} to reach front...")
        await asyncio.sleep(1)

    await ctx.reply(content=f"Your encode of {entry.filename} has begun.")

    avi_path = os.path.join(ENC_AVI_DIR, f"{entry.filename}.avi")
    mp4_path = os.path.join(ENC_AVI_DIR, f"{entry.filename}.mp4")

    # NOTE: Before encoding, delete the avi file if it exists.
    # If we don't we may leak data when a longer movie with the same name has been encoded previously
    if os.path.isfile(avi_path):
        os.remove(avi_path)

    if os.path.isfile(mp4_path):
        os.remove(mp4_path)

    args = [
        MUPEN_EXE,
        "--rom",
        os.path.join(DOWNLOAD_DIR, f"{entry.filename}.m64"),
        "--avi",
        avi_path
    ]

    if len(ENC_SM64_SCRIPTS) > 0:
        args += ["--lua", ENC_SM64_SCRIPTS]

    print(args)
    proc = await asyncio.create_subprocess_exec(*args)
    await proc.wait()

    # Sometimes avi files get created, but have only the header due to a crash on the first frame
    # We also check for that here
    if not os.path.isfile(avi_path) or os.path.getsize(avi_path) < 32:
        await ctx.reply(f"Failed to encode {entry.filename}.")
        return

    # Clamping: Figure out the correct ffmpeg params to fit the mp4 into 25 MB
    ffprobe_result = await ffprobe(avi_path)

    length_sec = float(ffprobe_result["format"]["duration"])
    filesize_limit = 8 * 25e6  # bits

    # cmd = f"-i encode.avi -c:v libx264 -c:a aac -vf fps=30 "
    total_bitrate = filesize_limit / length_sec

    if total_bitrate < 128000:
        await ctx.reply("Your movie is too large.")
        return

    audio_bitrate = min(16000 * math.floor(total_bitrate / 128000), 128000)
    video_bitrate = int((total_bitrate - audio_bitrate) * 0.95)

    ffmpeg_command = (
        FFmpegBuilder()
        .input(avi_path)
        .vcodec("libx264")
        .acodec("aac")
        .vfilter("fps=60,fps=30")  # prevents choppiness
        .vbv(video_bitrate, video_bitrate)
        .abr(audio_bitrate)
        .pix_fmt("yuv420p")
        .maxsize(int(filesize_limit * 0.95))
        .output(mp4_path)
    )

    print(ffmpeg_command)

    proc = await ffmpeg_command.run_async()
    await proc.wait()

    if proc.returncode != 0 or not os.path.isfile(mp4_path):
        await ctx.reply(f"Failed to encode {entry.filename}.")
        return

    await ctx.reply(file=discord.File(mp4_path), content=f"Your encode of {entry.filename} is ready!")


class Encode(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="encode", description="Encodes a movie and an optional savestate into a video file")
    async def encode(self, ctx, *args):

        # $encode queue shows the current queue

        if len(args) > 0 and args[0].lower() == "queue".lower():
            await send_queue(ctx)
            return

        if len(args) > 0 and args[0].lower() == "cancel".lower():
            await cancel_encode(ctx)
            return

        if len(encode_queue) >= ENC_MAX_QUEUE:
            await ctx.reply(
                content="The encode queue is currently full. Please try again later.".format(len(encode_queue),
                                                                                             ENC_MAX_QUEUE))
            return

        attachments = ctx.message.attachments
        movie_bytes = 0
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

            m64_idx = file_dict.get("m64")
            movie_path = f"{DOWNLOAD_DIR}/{attachments[m64_idx].filename}"
            print(movie_path)
            movie_bytes = await attachments[m64_idx].save(movie_path)

            if file_dict.get("st") is not None:
                st_idx = file_dict.get("st")
                st_path = f"{DOWNLOAD_DIR}/{attachments[st_idx].filename}"
                await attachments[st_idx].save(st_path)

            if file_dict.get("savestate") is not None:
                st_idx = file_dict.get("savestate")
                st_path = f"{DOWNLOAD_DIR}/{attachments[st_idx].filename}"
                await attachments[st_idx].save(st_path)

        if movie_bytes == 0:
            await ctx.reply("Failed to download the resources.")
            return

        # Stem of movie is also the stem of avi file
        # This is suspicious, but uses partition to grab the name before the first dot so the dot trick works
        filename = os.path.split(movie_path)[1].partition(".")[0]

        # When an st is provided, its stem must match the movie's stem
        if st_path is not None:
            # STs shouldn't have dots as well, so this is fine most likely. could be changed to first occurrence though
            st_stem = os.path.split(st_path)[1].rpartition(".")[0]
            if st_stem != filename:
                await ctx.reply("The provided savestate doesn't have the same name as the movie.")
                return

        entry = QueueEntry(uuid.uuid4(), filename, ctx.message.author, datetime.now(timezone.utc), None)
        encode_queue.append(entry)

        await ctx.reply(
            content=f"Your encode of {filename} has been added to the queue at position {len(encode_queue)}.")

        def pop_queue(_):
            print("Finished processing frontmost entry")
            encode_queue.pop(0)

        entry.task = asyncio.create_task(process_queue_front(ctx, entry))
        entry.task.add_done_callback(pop_queue)

    # @encode.error
    # async def encode_error(self, ctx, error):
    #     print(error)


async def setup(bot):
    await bot.add_cog(Encode(bot))
