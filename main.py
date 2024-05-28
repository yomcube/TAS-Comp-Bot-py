import os
import traceback
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands

# load environmental variables
load_dotenv()
token = os.getenv('TOKEN')

activity = discord.Game(name="Dolphin Emulator")

commands_ext = ['commands.dev.sync',
                'commands.db.start-task',
                'commands.db.end-task',
                'commands.db.edit-submissions',
                'commands.db.get-submissions',
                'commands.db.get-results',
                'commands.db.submit',
                'commands.db.info',
                'commands.help.help',
                'commands.misc.dm',
                'commands.misc.ping',
                'commands.misc.setname',
                'commands.fun.connect4',
                'commands.fun.addcoins',
                'commands.fun.balance',
                'commands.fun.rig',
                'commands.fun.freeiso',
                'commands.fun.slots',
                'commands.fun.say',
                'commands.settings.setsubmissionchannel',
                'commands.utilities.tracks',]
events_ext = ['events.on_ready',
              'events.on_message',
              'events.errors',
              'events.command_completion',]

# def get_prefix(bot, message):
#     #TODO:  code to get prefix
#     guild = message.guild
#     if guild is None:
#         return "" # returns no prefix if messaged in DMs; avoids on_message handling directly.
#     else:
#         return "$"

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$",
            intents=discord.Intents.all(),
            description='Python Discord bot for MKWii TAS Comp',
            activity=activity
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
bot.remove_command("help")

if __name__ == '__main__':
    bot.run(token)