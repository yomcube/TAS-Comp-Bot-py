import random

import discord
from discord.ext import commands
import shared

from api.submissions import count_submissions
from api.utils import is_task_currently_running, get_team_size, get_host_role


class TaskInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="task-info", aliases=['task-details'])
    async def info(self, ctx):
        current_task = await is_task_currently_running()

        if current_task is None:
            return await ctx.send("There is no ongoing task.")


        task_num, task_year, _, team_size, speed_task, _, deadline_timestamp, _ = current_task

        collab = f"Yes, {await get_team_size()} people" if team_size > 1 else "No"

        if deadline_timestamp is not None:
            deadline = f"<t:{deadline_timestamp}:f> (<t:{deadline_timestamp}:R>)"
        else:
            deadline = "Deadline has not been set by the host. See task channel."

        submissions = await count_submissions()

        host_role = self.bot.get_guild(shared.main_guild.id).get_role(await get_host_role(shared.main_guild.id))
        current_host = ", ".join([member.mention for member in host_role.members]) if host_role.members else "None"

        # Generate a random but vibrant color
        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        embed = discord.Embed(
            title=f"🏁 Task {task_num}, {task_year}",
            description=f"⏳ **Deadline:** {deadline}\n\u200B",
            color=embed_color
        )

        embed.add_field(name="👥 Collaboration", value=f"{collab}\n\u200B", inline=True)
        embed.add_field(name="⚡ Speed Task?", value=f"{'Yes' if speed_task else 'No'}\n\u200B", inline=True)
        embed.add_field(name="📩 Submissions", value=f"{submissions}\n\u200B", inline=True)
        embed.add_field(name="🎙️ Hosted by", value=current_host, inline=False)

        embed.set_footer(text="TAS Competition Info", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

        await ctx.send(embed=embed)




async def setup(bot):
    await bot.add_cog(TaskInfo(bot))
