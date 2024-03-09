import asyncio
import sys
import traceback
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from utils import download_attachments
from api import submissions

# load environmental variables
load_dotenv()
token = os.getenv('DISCORD_TOKEN')
download_dir = os.getenv('DOWNLOAD_DIR')
initial_extensions = ['commands.prefix',
                      'commands.encode']
if not os.path.isdir(download_dir):
    os.mkdir(download_dir)
    print(f"Created {download_dir}")


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            # TODO: Custom command prefixes
            command_prefix="$",
            intents=discord.Intents.all(),
            description="CompBot-py"
        )

    async def setup_hook(self):
        # Loading commands
        for extension in initial_extensions:
            await bot.load_extension(extension)


bot = Bot()


@bot.event
async def on_ready():
    print('Bot is ready!')


@bot.event
async def on_message(message) -> None:
    await bot.process_commands(message)
    # Handle DMs
    # Maybe there's a better way to handle this
    if isinstance(message.channel, discord.DMChannel):
        await submissions.handle_submissions(message)


@bot.event
async def on_command_completion(ctx):
    # TODO Handle command logs

    print("command done")


# Maybe there's a better way to do this, but this is error handling
@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
    ignored = ()
    error = getattr(error, 'original', error)
    if isinstance(error, ignored):
        return
    elif isinstance(error, commands.MissingPermissions):
        print("missing perms\n")
        return await ctx.send(f'You lack permissions to execute `{bot.command_prefix}{ctx.command}`.')
    elif isinstance(error, commands.NotOwner):
        print("not owner\n")
        return await ctx.send(f'Only the bot owner has permission to execute `{ctx.command}`.')
    elif isinstance(error, commands.CommandNotFound):
        return await ctx.send(f"{ctx.command} is not a valid command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(f"Missing fields in {ctx.command}.")
    print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot.run(token)
