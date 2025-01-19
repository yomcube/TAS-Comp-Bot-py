import discord
from discord.ext import commands
from api.utils import float_to_readable, has_host_role
from api.db_classes import Submissions, get_session
from sqlalchemy import select, update


class Edit(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="edit-submissions", description="Edit submissions", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, user: discord.Member, time: float, dq: bool, dq_reason: str = ''):
        async with get_session() as session:
            data = (await session.scalars(select(Submissions).where(Submissions.user_id == user.id))).first()

        if data is None:
            return await ctx.reply(f"{user} has no submission.",
                allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
        data_dq = None
        # was DQ or not
        if data.dq == 0:
            data_dq = False
        elif data.dq == 1:
            data_dq = True

        readable_time = float_to_readable(time)
        server_text = f"Succesfully edited {user}'s submission with:\nTime: from {data.time} to {time}\nDQ: from {data_dq} to {dq}"
        dm_text = f"Your submission has been edited:\nTime: from {float_to_readable(data.time)} to {readable_time}\nDQ: from {data_dq} to {dq}"

        if dq:
            server_text += f" ({dq_reason})"
            dm_text += f" ({dq_reason})"

        # Update submission to db
        async with get_session() as session:
            await session.execute(
                update(Submissions).values(time=time, dq=dq, dq_reason=dq_reason).where(Submissions.user_id == user.id))
            await session.commit()

        await ctx.reply(server_text,
            allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
        channel = await user.create_dm()
        await channel.send(dm_text,
            allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)



async def setup(bot) -> None:
    await bot.add_cog(Edit(bot))
