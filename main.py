import os
import traceback
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands

# load environmental variables
load_dotenv()
token = os.getenv('TOKEN')

if not os.path.exists("database"): 
    os.makedirs("database")

activity = discord.Game(name="Dolphin Emulator")

commands_ext = ['commands.db.host.start-task',
                'commands.db.host.end-task',
                'commands.db.host.edit-submissions',
                'commands.db.host.get-submissions',
                'commands.db.host.get-results',
                'commands.db.host.submit',
                'commands.db.admin.rig',
                'commands.db.admin.set-host-role',
                'commands.db.admin.set-submission-channel',
                'commands.db.info',
                'commands.db.setname',
                'commands.fun.8ball',
                'commands.fun.addcoins',
                'commands.fun.balance',
                'commands.fun.coinflip',
                'commands.fun.connect4',
                'commands.fun.dashsupersecretcommand',
                'commands.fun.joke',
                'commands.fun.freeiso',
                'commands.fun.rockpaperscissors',
                'commands.fun.shadowsupersecretcommand',
                'commands.fun.slots',
                'commands.utilities.host.dm',
                'commands.utilities.admin.say',
                'commands.utilities.admin.sync',
                'commands.utilities.manage_messages.clear',
                'commands.utilities.help',
                'commands.utilities.prefix',
                'commands.utilities.track',
                'commands.utilities.weather',
                'commands.utilities.urban',]
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
