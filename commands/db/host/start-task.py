import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from api.submissions import get_submission_channel
from api.task_handling import start_task
from api.utils import has_host_role, get_submitter_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

async def remove_submitter_role(bot, guild_id: int) -> None:
    # Also clear submitter roles
    submitter_role = await get_submitter_role(DEFAULT)
    server = bot.get_guild(guild_id)
    role = server.get_role(submitter_role)

    for member in role.members:
        try:
            await member.remove_roles(role)
        except discord.Forbidden:
            print(
                f"Failed to remove role {role.name} from {member.display_name} due to insufficient permissions.")
        except discord.HTTPException as e:
            print(f"Failed to remove role {role.name} from {member.display_name} due to an error: {e}")

async def delete_previous_current_submissions(bot) -> None | str:
    # Delete previous "Current submissions" message in submission channel
    channel_id = await get_submission_channel(DEFAULT)
    channel = bot.get_channel(channel_id)

    try:
        async for message in channel.history(limit=5):  # Adjust limit as necessary
            if message.author == bot.user:
                await message.delete()
                break

    except AttributeError:
        return "Please set the submission channel with `/set-submission-channel`! (Ask an admin if you do not have permission)"


class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, team_size: int = 1, multiple_tracks: int = 0,
                      speed_task: int = 0, year: int = None, deadline: int = None):
        await ctx.defer()
        result = await start_task(number, team_size, multiple_tracks,
                                  speed_task, year, deadline, ctx.guild.id, ctx.message.guild.id)
        if result is True:
            # Delete previous "Current submissions" message in submission channel
            # Only not none if there is an error in doing this
            if await delete_previous_current_submissions(self.bot, ctx.guild.id) is not None:
                return await ctx.send(await delete_previous_current_submissions(self.bot, ctx.guild.id))

            # Successful message to send:
            if deadline is not None:
                await ctx.send(f"Successfully started **Task {number} - {year}**! Deadline: <t:{deadline}:f>")
            else:
                await ctx.send(f"Successfully started **Task {number} - {year}**!")

            # Remove the submitter role from all members
            await remove_submitter_role(self.bot, ctx.guild.id, ctx.author.id)
        return None

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
