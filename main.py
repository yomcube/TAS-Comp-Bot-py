import os
import traceback
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands

# load environmental variables
load_dotenv()
token = os.getenv('TOKEN')

commands_ext = ['commands.dev.sync',
                'commands.db.start-task',
                'commands.db.submit',
                'commands.db.info',
                'commands.fun.ping',
                'commands.fun.slots',
                'commands.fun.say',
                'commands.utilities.tracks',]
events_ext = ['events.on_ready',
              'events.on_message',
              'events.errors',
              'events.command_completion',]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='$',
            intents=discord.Intents.all(),
            description='Python Discord bot for MKWii TAS Comp'
        )

    async def setup_hook(self):
        # Loading commands
        for command in commands_ext:
            try:
                await self.load_extension(command)
            except Exception as e:
                print(f'Failed to load {command}.', file=sys.stderr)
                traceback.print_exc()

        # Loading events
        for event in events_ext:
            try:
                await self.load_extension(event)
            except Exception as e:
                print(f'Failed to load {event}.', file=sys.stderr)
                traceback.print_exc()

bot = Bot()

if __name__ == '__main__':
    bot.run(token)