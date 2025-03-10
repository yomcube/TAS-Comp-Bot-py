import os
import time
import math

from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import select, update

from api.db_classes import get_session, Tasks
from api.utils import has_host_role

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Setdeadline(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-deadline",
                             description="Adjust or set the deadline after the task has started", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, deadline: int):

        if deadline < int(time.time()):
            return await ctx.send("This deadline is in the past! Retry again.")

        # if deadline is valid, round it up to nearest minute
        deadline = math.ceil(deadline / 60) * 60


        async with get_session() as session:
            query = select(Tasks.deadline).where(Tasks.is_active == 1)
            result = (await session.execute(query)).first()
            if result is None:
                return await ctx.send("There is no active task.")

            stmt = update(Tasks).values(deadline=deadline).where(Tasks.is_active == 1)
            await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The deadline has been set to <t:{deadline}:F> (<t:{deadline}:R>) for the current task.")


async def setup(bot) -> None:
    await bot.add_cog(Setdeadline(bot))
