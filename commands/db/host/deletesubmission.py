import discord
from discord.ext import commands
from api.utils import has_host_role
from api.db_classes import Submissions, get_session, Tasks
from api.submissions import get_submission_channel, get_display_name, generate_submission_list
from sqlalchemy import select, delete
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def reorder_primary_keys():
    async with get_session() as session:

        # Retrieve the submissions
        query = select(Submissions).order_by(Submissions.index)
        result = await session.execute(query)
        submissions = result.scalars().all()

        # Reassign indexes
        for idx, submission in enumerate(submissions, start=1):
            submission.index = idx

        await session.commit()

class DeleteSubmission(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="delete-submission", description="Delete someone's submission", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, user: discord.Member):
        async with get_session() as session:
            currently_running = (await session.execute(select(Tasks).where(Tasks.is_active == 1))).first()
            if not currently_running:
                return await ctx.send("There is no ongoing task")

        async with get_session() as session:
            data = (await session.scalars(select(Submissions).where(Submissions.user_id == user.id))).first()

        if data is None:
            return await ctx.reply(f"{user} has no submission.")

        # Delete submission from db
        async with get_session() as session:
            await session.execute(delete(Submissions).where(Submissions.user_id == user.id))
            await session.commit()


        # Re-arrange the indexes in the submission table so that they are no gaps between numbers
        await reorder_primary_keys()

        # Update submission list
        await generate_submission_list(self)


        await ctx.send(f"{user.display_name}'s submission has been deleted.")


async def setup(bot) -> None:
    await bot.add_cog(DeleteSubmission(bot))
