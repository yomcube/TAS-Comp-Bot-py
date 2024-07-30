import os
import discord
from discord.ext import commands
from api.db_classes import get_session, SpeedTaskTime
from api.utils import has_host_role
from sqlalchemy import select, insert, update
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Speedtasktime(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-time", aliases=['stt'],
                             description="Set the time users have to submit to speed tasks", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, time: float, comp: str = DEFAULT):

        # TODO: detect which server you are in, so the comp argument is no longer needed
        async with get_session() as session:
            query = select(SpeedTaskTime.time).where(SpeedTaskTime.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()
            if result is None:
                stmt = insert(SpeedTaskTime).values(guild_id=ctx.message.guild.id, time=time, comp=comp)
                await session.execute(stmt)

            else:
                stmt = update(SpeedTaskTime).values(guild_id=ctx.message.guild.id, time=time, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The speed task time has been set to **{time}** hours! ")


async def setup(bot) -> None:
    await bot.add_cog(Speedtasktime(bot))
