from discord.ext import commands
from api.utils import has_host_role, session
from api.db_classes import Tasks
from sqlalchemy import select, update


class End(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="end-task", description="End current task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):

        currently_running = (await session.execute(select(Tasks.task, Tasks.year).where(Tasks.is_active == 1))).first()
        # Is a task running?

        if currently_running:
            number = currently_running.task
            year = currently_running.year
            await session.execute(update(Tasks).values(is_active=0).where(Tasks.is_active == 1))
            await session.commit()

            await ctx.send(f"Successfully ended **Task {number} - {year}**!")
        else:
            await ctx.send(f"There is already no ongoing task!")


async def setup(bot) -> None:
    await bot.add_cog(End(bot))
