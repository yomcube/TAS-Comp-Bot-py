import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import insert, update, select

from api.db_classes import SubmitterRole, get_session

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class SetSubmitterrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-submitter-role", aliases=['ssr'], description="Set the current submitter role",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role, comp: str = DEFAULT):
        async with get_session() as session:
            submitter_role = (await session.scalars(select(SubmitterRole.comp).where(SubmitterRole.comp == comp))).first()
            name = role.name
            role_id = role.id

            # Check if submitter_role doesn't exist yet for the comp
            if submitter_role is None:
                stmt = (insert(SubmitterRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
                await session.execute(stmt)
            else:

                stmt = (update(SubmitterRole).values(role_id=role_id, name=name).where(SubmitterRole.comp == comp))
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The submitter role has been set! {role.mention}")


async def setup(bot) -> None:
    await bot.add_cog(SetSubmitterrole(bot))
