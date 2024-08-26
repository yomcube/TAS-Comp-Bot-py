from discord.ext import commands
from api.utils import float_to_readable, has_host_role
from api.submissions import get_display_name, is_in_team, get_team_ids, get_team_members, get_team_name
from api.db_classes import Submissions, get_session
from sqlalchemy import select


class Results(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="get-results", description="Get the ordered results", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        async with get_session() as session:
            active_task = (await session.scalars(select(Submissions.task))).first()
            # Get all submissions ordered by time
            submissions = (await session.scalars(select(Submissions).where(Submissions.task == active_task,
                                                                           Submissions.dq == 0).order_by(
                Submissions.time.asc()))).fetchall()

            # Get all DQs ordered by time
            DQs = (await session.scalars(select(Submissions).where(Submissions.task == active_task,
                                                                   Submissions.dq == 1).order_by(
                Submissions.time.asc()))).fetchall()

        content = f"**__Task {active_task} Results__**:\n\n"

        for (n, submission) in enumerate(submissions, start=1):
            if await is_in_team(submission.user_id):
                ids = await get_team_ids(submission.user_id)
                members = await get_team_members(ids)
                team_name = await get_team_name(submission.user_id)

                name = f'{team_name} ({" & ".join(members)})'
            else:
                name = await get_display_name(submission.user_id)

            readable_time = float_to_readable(submission.time)
            content += f'{n}. {name} — {readable_time}\n'

        # add return incase of DQs.
        content += '\n'

        # Rank DQs in order
        for run in DQs:
            display_name = await get_display_name(run.user_id)
            readable_time = float_to_readable(run.time)
            dq_reason = run.dq_reason
            content += f'DQ. {display_name} — {readable_time} [{dq_reason}]\n'

        await ctx.send(content)

        #except TypeError: # can happen if get_display_name throws an error; an id is not found in user.db
        # Happens, for example, if an admin /submit for someone who is not in the user.db
        #await ctx.send("Someone's result could not be retrieved.")


async def setup(bot) -> None:
    await bot.add_cog(Results(bot))
