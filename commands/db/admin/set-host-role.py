import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import insert, update, select
from api.db_classes import HostRole, session, Base
load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Sethostrole(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="set-host-role", aliases=['shr'], description="Set the current host role",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, role: discord.Role, comp: str = DEFAULT):
        host_role = session.scalars(select(HostRole.comp).where(HostRole.comp == comp)).first()
        name = role.name
        role_id = role.id

        # Check if host_role doesn't exist yet for the comp
        if host_role is None:
            print(host_role)
            stmt = (insert(HostRole).values(role_id=role_id, name=name, comp=comp, guild_id=ctx.guild.id))
            session.execute(stmt)
        else:

            stmt = (update(HostRole).values(role_id=role_id, name=name).where(HostRole.comp == comp))
            session.execute(stmt)

        session.commit()
        await ctx.send(f"The current host role has been set! {role.mention}")

        #except sqlite3.OperationalError as e:
         #   print(e)
          #  connection.close()
           # await ctx.send("An error occured.")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
