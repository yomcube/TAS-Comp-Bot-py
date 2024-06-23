from discord.ext import commands
from api.db_classes import Teams, get_session
from api.utils import is_in_team, get_team_size
from sqlalchemy import select, delete


class ImFree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_users = {}
        self.ctx = None
        self.author = None
        self.team_size = None

    @commands.hybrid_command(name="teamfree", aliases=["imfree"], description="Set yourself as \"free\" so you appear as it in the team leaderboard", with_app_command=True)
    async def free(self, ctx):
        self.ctx = ctx
        self.author = ctx.author
        self.team_size = await get_team_size()
        
        # Is there a task running?
        if self.team_size is None:
            return await ctx.send("There is no task running currently.")

        # Verify if it's indeed a collab task
        elif self.team_size < 2:
            return await ctx.send("This is a solo task. You may **not** collaborate!")
        
        # Make sure they are not already in a team
        if await is_in_team(ctx.author.id):
            return await ctx.send("You are already in a team.")
        
        pass
                

async def setup(bot):
    await bot.add_cog(ImFree(bot))