import os
import discord
from discord.ext import commands
from api.db_classes import get_session, SpeedTaskDesc
from api.utils import has_host_role
from sqlalchemy import select, insert, update
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Speedtaskdesc(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-desc", aliases=['std'],
                             description="Set the description of the speed tasks", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, desc: str, comp: str = DEFAULT):

        # TODO: detect which server you are in, so the comp argument is no longer needed
        async with get_session() as session:
            query = select(SpeedTaskDesc.desc).where(SpeedTaskDesc.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()
            if result is None:
                stmt = insert(SpeedTaskDesc).values(guild_id=ctx.message.guild.id, desc=desc, comp=comp)
                await session.execute(stmt)

            else:
                stmt = update(SpeedTaskDesc).values(guild_id=ctx.message.guild.id, desc=desc, comp=comp)
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The speed task description has been set! \n{desc}")


async def setup(bot) -> None:
    await bot.add_cog(Speedtaskdesc(bot))
