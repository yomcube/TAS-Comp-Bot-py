import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import insert, update, select
from api.db_classes import HostRole, get_session
load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Sethostrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-host-role", aliases=['shr'], description="Set the current host role",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role, comp: str = DEFAULT):
        async with get_session() as session:
            host_role = (await session.scalars(select(HostRole.comp).where(HostRole.comp == comp))).first()
            name = role.name
            role_id = role.id

            # Check if host_role doesn't exist yet for the comp
            if host_role is None:
                stmt = (insert(HostRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
                await session.execute(stmt)
            else:

                stmt = (update(HostRole).values(role_id=role_id, name=name).where(HostRole.comp == comp))
                await session.execute(stmt)

            await session.commit()

        await ctx.send(f"The current host role has been set! {role.mention}")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
