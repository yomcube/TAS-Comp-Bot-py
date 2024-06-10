from discord.ext import commands
from api.submissions import get_display_name
from api.utils import has_host_role, float_to_readable, session
from api.db_classes import Submissions
from sqlalchemy import select


class Get(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-submissions", description="Get submissions for current task",
                             with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        # Get current task by taking random submission, and extracting task number
        active_task = session.scalars(select(Submissions.task).limit(1)).first()

        if active_task is None:
            await ctx.send("There were no submissions.")
            return

        # Get submissions from current task

        submissions = session.scalars(select(Submissions).where(Submissions.task == active_task)).fetchall()
        total_submissions = len(submissions)
        # Count submissions from current task

        content = f"__Task {active_task} submissions__:\n(Total submissions: {total_submissions})\n\n"

        # Add many lines depending on the number of submissions
        try:
            for submission in submissions:
                content += (f"{get_display_name(submission.user_id, ctx.message.guild.id)} : {submission.url}"
                            f" | Fetched time: ||{float_to_readable(submission.time)}||\n")

            await ctx.reply(content=content)

        except TypeError:  # can happen if get_display_name throws an error; an id is not found in user.db
            # Happens, for example, if an admin /submit for someone who is not in the user.db
            await ctx.send("Someone's submission could not be retrieved.")


async def setup(bot) -> None:
    await bot.add_cog(Get(bot))
