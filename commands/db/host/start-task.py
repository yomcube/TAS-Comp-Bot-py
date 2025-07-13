import os

from discord.ext import commands
from dotenv import load_dotenv

from api.task_handling import start_task
from api.utils import has_host_role
from discord_ext.discord_utils import delete_previous_current_submissions, remove_submitter_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, team_size: int = 1, multiple_tracks: int = 0,
                      speed_task: int = 0, year: int = None, deadline: int = None) -> None:
        await ctx.defer()
        await start_task(number, team_size, multiple_tracks,
                         speed_task, year, deadline, ctx.guild.id, ctx.message.guild.id)
        # Delete previous "Current submissions" message in submission channel
        await delete_previous_current_submissions(self.bot)

        # Successful message to send:
        if deadline is not None:
            await ctx.send(f"Successfully started **Task {number} - {year}**! Deadline: <t:{deadline}:f>")
        else:
            await ctx.send(f"Successfully started **Task {number} - {year}**!")

        # Remove the submitter role from all members
        await remove_submitter_role(self.bot, ctx.guild.id)

        ######################
        #### TEAMS SYSTEM ####
        ######################
        # try:
        #     seeking_channel_id = await get_seeking_channel(DEFAULT)
        #     seeking_channel = self.bot.get_channel(seeking_channel_id)
        #
        #
        #     # unpin old teams message
        #     pinned_messages = await seeking_channel.pins()
        #     bot_pinned_messages = [msg for msg in pinned_messages if msg.author == self.bot.user]
        #
        #     await bot_pinned_messages[-1].unpin()
        #
        # except AttributeError:
        #     await ctx.send(f"Please set the seeking channel with `/set-seeking-channel`! (Ask an admin if you do not have permission)")
        #
        # except IndexError:
        #     print("No message from bot to unpin")
        #
        #
        # team_size = await get_team_size()
        #
        # # Verify if it's indeed a collab task
        # if team_size < 2:
        #     return
        #
        #
        # teams_content = "__**Confirmed teams:**__\n"
        #
        # try:
        #
        #     final_message = await seeking_channel.send(f"{teams_content}")
        #     await final_message.pin()
        #
        #
        # except AttributeError:
        #     await ctx.send(f"Please set the seeking channel with `/set-seeking-channel`! (Ask an admin if you do not have permission)")


async def setup(bot) -> None:
    await bot.add_cog(Start(bot))
