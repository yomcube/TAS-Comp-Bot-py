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
        host_role = session.scalars(select(HostRole.comp).where(HostRole.comp is comp)).first()
        name = role.name
        role_id = role.id

        # Check if host_role doesn't exist yet for the comp
        if host_role is None:
            print(host_role)
            stmt = (insert(HostRole).values(role_id=role_id, name=name, comp=comp))
            session.execute(stmt)
        else:

            stmt = (update(HostRole).values(role_id=role_id, name=name, comp=comp))
            session.execute(stmt)

        session.commit()

            #cursor.execute("SELECT * FROM host_role WHERE comp = ?", (comp,))
            #existing = cursor.fetchone()

            #if existing:
             #   cursor.execute('UPDATE host_role SET name = ?,id = ? WHERE comp = ?', (name, id, comp,))
            #else:
             #   cursor.execute('INSERT INTO host_role (comp, name, id) VALUES (?, ?, ?)', (comp, name, id,))

            # Commit whatever change
            #connection.commit()
            #connection.close()

        await ctx.send(f"The current host role has been set! {role.mention}")

        #except sqlite3.OperationalError as e:
         #   print(e)
          #  connection.close()
           # await ctx.send("An error occured.")


async def setup(bot) -> None:
    await bot.add_cog(Sethostrole(bot))
