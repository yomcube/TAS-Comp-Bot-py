import asyncio
import os
import traceback
import sys
from dotenv import load_dotenv
import discord
from discord.ext import commands

from api.db_classes import db_connect

# load environmental variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
DB_DIR = os.path.abspath(os.getenv('DB_DIR'))

os.makedirs(DB_DIR) if not os.path.exists(DB_DIR) else None
activity = discord.Game(name="Dolphin Emulator")

commands_ext = ['commands.db.host.start-task',
                'commands.db.host.end-task',
                'commands.db.host.deletesubmission',
                'commands.db.host.edit-submissions',
                'commands.db.host.get-submissions',
                'commands.db.host.get-results',
                'commands.db.host.submit',
                'commands.db.admin.rig',
                'commands.db.admin.set-host-role',
                'commands.db.admin.set-logs-channel',
                'commands.db.admin.set-submission-channel',
                'commands.db.admin.set-seeking-channel',
                'commands.db.admin.config',
                'commands.db.admin.fake-collab',
                'commands.db.info',
                'commands.db.setname',
                'commands.db.team.collab',
                'commands.db.team.leaveteam',
                'commands.db.team.hostdissolve',
                'commands.fun.8ball',
                'commands.fun.addcoins',
                'commands.fun.balance',
                'commands.fun.balancetop',
                'commands.fun.coinflip',
                'commands.fun.connect4',
                'commands.fun.dashsupersecretcommand',
                'commands.fun.giveqm',
                'commands.fun.joke',
                'commands.fun.freeiso',
                'commands.fun.rockpaperscissors',
                'commands.fun.shadowsupersecretcommand',
                'commands.fun.slots',
                'commands.fun.tomcubesupersecretcommand',
                'commands.utilities.host.dm',
                'commands.utilities.admin.say',
                'commands.utilities.admin.sync',
                'commands.utilities.credits',
                'commands.utilities.help',
                'commands.utilities.manage_messages.clear',
                'commands.utilities.music',
                'commands.utilities.prefix',
                'commands.utilities.track',
                'commands.utilities.weather',
                'commands.utilities.urban',
                'commands.utilities.ping',
                'commands.sm64.encode', ]
events_ext = ['events.on_ready',
              'events.on_message',
              'events.errors',
              'events.command_completion', ]


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


def main():
    bot = Bot()
    bot.remove_command("help")
    asyncio.run(db_connect())
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
