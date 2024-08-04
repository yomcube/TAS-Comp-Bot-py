from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from datetime import date
from api.utils import is_task_currently_running, has_host_role, get_team_size
from api.submissions import get_submission_channel, get_seeking_channel
from api.db_classes import Tasks, Submissions, Teams, SpeedTask, get_session
from sqlalchemy import insert, delete, select

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, team_size: int = 1, multiple_tracks: int = 0,
                      speed_task: int = 0, year: int = None):

        if not year:
            year = date.today().year

        if await is_task_currently_running() is None:
            async with get_session() as session:
                # Mark task as ongoing
                await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                           multiple_tracks=multiple_tracks, speed_task=speed_task))

                # Clear submissions from previous task, as well as potential teams, and speed task table
                await session.execute(delete(Submissions))
                await session.execute(delete(Teams))
                await session.execute(delete(SpeedTask))

                # Commit changes to both tables affected
                await session.commit()

            # Delete previous "Current submissions" message in submission channel
            channel_id = await get_submission_channel(DEFAULT)
            channel = self.bot.get_channel(channel_id)

            try:
                async for message in channel.history(limit=5):  # Adjust limit as necessary
                    if message.author == self.bot.user:
                        await message.delete()
                        break

            except AttributeError:
                await ctx.send(
                    "Please set the submission channel with `/set-submission-channel`! (Ask an admin if you do not have permission)")

            await ctx.send(f"Successfully started **Task {number} - {year}**!")

        else:
            # if a task is already ongoing...
            await ctx.send(f"A task is already ongoing.\nPlease use `/end-task` to end the current task.")
            return
        
        
        
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
