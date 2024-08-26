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

        header = f"__Task {active_task} submissions__:\n(Total submissions: {total_submissions})\n\n"
        await ctx.send(header)

        # Send all submissions
        try:
            for submission in submissions:
                if await is_in_team(submission.user_id):
                    ids = await get_team_ids(submission.user_id)
                    members = await get_team_members(ids)
                    team_name = await get_team_name(submission.user_id)

                    name = f'{team_name} ({" & ".join(members)})'
                else:
                    name = await get_display_name(submission.user_id)

                content = (f"{name} : {submission.url}"
                            f" | Fetched time: ||{float_to_readable(submission.time)}||\n")
                await ctx.send(content=content)
                await asyncio.sleep(0.5)



        except TypeError as e:  # can happen if get_display_name throws an error; an id is not found in user.db
            # Happens, for example, if an admin /submit for someone who is not in the user.db
            print(e)
            await ctx.send("Someone's submission could not be retrieved.")


async def setup(bot) -> None:
    await bot.add_cog(Get(bot))
