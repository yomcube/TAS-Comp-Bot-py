import os
from dotenv import load_dotenv
from discord.ext import commands
from api.utils import has_host_role
from api.db_classes import Tasks, get_session, SpeedTaskDesc
from sqlalchemy import select, update, delete

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class End(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="end-task", description="End current task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx):
        async with get_session() as session:
            currently_running = (await session.execute(select(Tasks.task, Tasks.year).where(Tasks.is_active == 1))).first()
            
        # Is a task running?
        if currently_running:
            async with get_session() as session:

                number = currently_running.task
                year = currently_running.year
                await session.execute(update(Tasks).values(is_active=0).where(Tasks.is_active == 1))
                
                # Delete the task -- we don't really need to keep, and delete speed task desc
                await session.execute(delete(Tasks).where(Tasks.is_active == 0))
                await session.execute(delete(SpeedTaskDesc))
                
                await session.commit()


            await ctx.send(f"Successfully ended **Task {number} - {year}**!")
        else:
            await ctx.send(f"There is already no ongoing task!")


async def setup(bot) -> None:
    await bot.add_cog(End(bot))
