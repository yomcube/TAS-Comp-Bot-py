from discord.ext import commands
import discord
import os
import time
from dotenv import load_dotenv
from datetime import date
from api.utils import is_task_currently_running, has_host_role, get_team_size
from api.submissions import get_submission_channel, get_seeking_channel
from api.db_classes import Tasks, Submissions, Teams, SpeedTask, get_session, SpeedTaskLength
from sqlalchemy import insert, delete, select
import math

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, team_size: int = 1, multiple_tracks: int = 0,
                      speed_task: int = 0, year: int = None, deadline: int = None):


        if deadline is not None:
            # Prevent a task from creating if deadline is in the past
            if deadline < int(time.time()):
                return await ctx.send("This deadline is in the past! Retry again.")

            else: # if deadline is valid, round it up to nearest minute
                deadline = math.ceil(deadline / 60) * 60

        # auto set year
        if not year:
            year = date.today().year

        if await is_task_currently_running() is None:
            async with get_session() as session:

                # Insert task in database. Non speed task case (difference is the is-released parameter)
                if speed_task == 0:
                    await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                               multiple_tracks=multiple_tracks, speed_task=speed_task,
                                                               deadline=deadline, is_released=1))


                # Insert task in database. Speed task case
                else:
                    await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                               multiple_tracks=multiple_tracks, speed_task=speed_task,
                                                               deadline=deadline, is_released=0))

                    # If a speed task and there is no default task duration set, set it to 4h.
                    query = select(SpeedTaskLength.time).where(SpeedTaskLength.guild_id == ctx.guild.id)
                    task_duration = (await session.scalars(query)).first()

                    if task_duration is None:
                        stmt = insert(SpeedTaskLength).values(guild_id=ctx.message.guild.id, time=4.0, comp=DEFAULT)
                        await session.execute(stmt)
                        await session.commit()



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



            # Successful message to send:
            if deadline is not None:
                await ctx.send(f"Successfully started **Task {number} - {year}**! Deadline: <t:{deadline}:f>")
            else:
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
