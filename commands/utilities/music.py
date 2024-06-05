import discord
from discord.ext import commands
import yt_dlp
import asyncio

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                      'options': '-vn -filter:a "volume=0.25"'}

ffmpeg_path = './ffmpeg/ffmpeg.exe'


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="joinvc", description="Make the bot join your VC channel.", with_app_command=True)
    async def joinvc(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)
            await channel.connect()
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.hybrid_command(name="play", description="Play the sound of a youtube video in a VC!", with_app_command=True)
    async def play(self, ctx, url):
        try:
            if ctx.voice_client is not None:
                voice_client = ctx.voice_client
            else:
                voice_client = await ctx.author.voice.channel.connect()

            voice_clients[ctx.guild.id] = voice_client

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegPCMAudio(song, executable=ffmpeg_path, **ffmpeg_options)

            if not voice_clients[ctx.guild.id].is_playing():
                voice_clients[ctx.guild.id].play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send(f'Now playing: {data["title"]}')
            else:
                await ctx.send('Already playing a song! Use `$stop` to stop the current song first.')
        except Exception as e:
            print(f'Error: {e}')

    @commands.hybrid_command(name="leave", description="Kick the bot ouf of your VC channel.", with_app_command=True)
    async def leave(self, ctx):
        if ctx.voice_client:
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