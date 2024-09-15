from discord.ext import commands
from api.submissions import get_display_name, get_team_ids, get_team_members, get_team_name
from api.utils import has_host_role, float_to_readable, is_in_team
from api.db_classes import Submissions, get_session
from sqlalchemy import select
import asyncio


class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task",
                             with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        # Get current task by taking random submission, and extracting task number
        async with get_session() as session:
            active_task = (await session.scalars(select(Submissions.task).limit(1))).first()

        if active_task is None:
            await ctx.send("There were no submissions.")
            return

        # Get submissions from current task
        async with get_session() as session:
            submissions = (await session.scalars(select(Submissions).where(Submissions.task == active_task))).fetchall()
            total_submissions = len(submissions)
        # Count submissions from current task

        # Send all submissions and truncate if > 2000
        try:
            msg_limit = 2000
            buffer = 50  # Small buffer to prevent exceeding the limit
            submissions_parts = []
            current_part = ""

            for submission in submissions:
                if await is_in_team(submission.user_id):
                    ids = await get_team_ids(submission.user_id)
                    members = await get_team_members(ids)
                    team_name = await get_team_name(submission.user_id)

                    name = f'{team_name} ({" & ".join(members)})'
                else:
                    name = await get_display_name(submission.user_id)

                submission_text = f"{submissions.index(submission) + 1}. {name} : {submission.url} | Fetched time: ||{float_to_readable(submission.time)}||\n"

                # Check if adding this submission would exceed the message limit
                if len(current_part) + len(submission_text) > (msg_limit - buffer):
                    submissions_parts.append(current_part)  # Save the current part
                    current_part = submission_text  # Start a new part
                else:
                    current_part += submission_text

            # Append the last part
            if current_part:
                submissions_parts.append(current_part)

            header = f"__**Task {active_task} submissions**__:\n-# (Total submissions: {total_submissions})\n\n"

            # Send the messages, including the header in the first message
            for i, part in enumerate(submissions_parts):
                if i == 0:
                    if len(header + part) > msg_limit:
                        await ctx.reply(header)
                        await ctx.reply(part)
                    else:
                        await ctx.reply(header + part)
                else:
                    await ctx.reply(part)

                await asyncio.sleep(1)

        except TypeError as e:
            print(e)
            await ctx.send("Someone's submission could not be retrieved.")



async def setup(bot) -> None:
    await bot.add_cog(Get(bot))