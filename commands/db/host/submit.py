import os

from discord.ext import commands
import discord
from dotenv import load_dotenv
from sqlalchemy import insert, update

from api.utils import is_task_currently_running, readable_to_float, has_host_role
from api.submissions import (first_time_submission, generate_submission_list,
    new_competitor, post_submission_list, get_display_name, get_submission_channel)
from api.mkwii.mkwii_utils import get_lap_time, get_character, get_vehicle
from api.db_classes import Submissions, get_session, Userbase

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class Submit(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name='submit', description='Submit', with_app_command=True)
    @has_host_role()
    async def submit(self, ctx, user: discord.Member, file: discord.Attachment):
        if not user:
            user = ctx.author

        current_task = await is_task_currently_running()
        url = file.url

        # retrieving lap time, to estimate submission time

        rkg_data = await file.read()

        try:
            rkg = bytearray(rkg_data)
            if rkg[:4] == b'RKGD':
                lap_times = get_lap_time(rkg)

                # float time to upload to db
                time = readable_to_float(lap_times[0])  # For most (but not all) mkw single-track tasks, the first
                # lap time is usually the time of the submission, given the task is on lap 1 and not backwards.

                character = get_character(rkg)
                vehicle = get_vehicle(rkg)

            else:
                time = 0
                character = None
                vehicle = None
                await ctx.reply("Invalid RKG file format")
                return

        except UnboundLocalError:
            # This exception catches blank rkg files
            time = 0
            character = None
            vehicle = None
            await ctx.reply("Nice blank rkg there")
            return

        async with get_session() as session:
            # If it's new competitor, add to userbase first
            if await new_competitor(user.id):
                await session.execute(
                    insert(Userbase).values(user_id=user.id, user=user.name, display_name=user.display_name))

                await session.commit()



            # Check if user has already submitted
            if await first_time_submission(user.id):
                query = insert(Submissions).values(task=current_task[0], name=user.name, user_id=user.id, url=url, time=time,
                                                   dq=0, dq_reason='', character=character, vehicle=vehicle)
                await session.execute(query)
                await session.commit()
            else:
                query = (update(Submissions).values(url=url, time=time, character=character, vehicle=vehicle)
                         .where(Submissions.user_id == user.id))
                await session.execute(query)
                await session.commit()

        # If the submission list is already generated (most cases)
        try:
            await generate_submission_list(self)

        # First submission of the task
        except UnboundLocalError:
            submission_channel = self.bot.get_channel(await get_submission_channel(DEFAULT))
            display_name = await get_display_name(user.id)

            await post_submission_list(submission_channel, user.id, display_name)

        await ctx.reply(f"A submission has been added for {user.name}!")


async def setup(bot) -> None:
    await bot.add_cog(Submit(bot))
