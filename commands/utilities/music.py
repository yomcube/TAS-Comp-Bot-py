import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
import asyncio

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
}

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="joinvc", description="Make the bot join your VC channel.", with_app_command=True)
    async def joinvc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel

            # Check if the bot is already in a voice channel
            if ctx.voice_client:
                # Move the bot to the new channel
                await ctx.voice_client.disconnect()
                await channel.connect()
            else:
                # Connect the bot to the channel
                await channel.connect()

            # Reference the voice client explicitly
            vc = ctx.voice_client

            # Play the sound file
            if DEFAULT == 'mkw':
                source = discord.FFmpegPCMAudio('./commands/utilities/mkwii/on_join.wav')
                vc.play(source)
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.hybrid_command(name="play", description="Play the sound of a youtube video in a VC!", with_app_command=True)
    async def play(self, ctx, url):
        try:
            if ctx.voice_client is not None:
                voice_client = ctx.voice_client
            else:
                return await ctx.send("I am not in a voice chat! Invite me by doing `$joinvc`.")

            voice_clients[ctx.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

            if not voice_clients[ctx.guild.id].is_playing():
                voice_clients[ctx.guild.id].play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send(f'Now playing: {data["title"]}')
            else:
                await ctx.send('Already playing a song! Use `$stop` to stop the current song first.')
        except Exception as e:
            print(f'Error: {e}')

    @commands.hybrid_command(name="leave-vc", description="Kick the bot out of your VC channel.", with_app_command=True)
    async def leave(self, ctx):
        if ctx.voice_client:

            if DEFAULT == 'mkw':
                # Funky kong sends his farewells
                source = discord.FFmpegPCMAudio('./commands/utilities/mkwii/on_leave.wav')
                ctx.voice_client.play(source)
                await asyncio.sleep(7)

            await ctx.voice_client.disconnect()
            voice_clients.pop(ctx.guild.id, None)
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not connected to a voice channel.")

    @commands.hybrid_command(name="stop", description="Stop the ongoing video", with_app_command=True)
    async def stop(self, ctx):
        if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
            voice_clients[ctx.guild.id].stop()
            await ctx.send('Stopped the current song.')
        else:
            await ctx.send('No song is currently playing.')


async def setup(bot) -> None:
    await bot.add_cog(Music(bot))