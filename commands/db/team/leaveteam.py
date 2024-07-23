import discord
from discord.ext import commands
from api.db_classes import Teams, get_session
from sqlalchemy import select, delete

class AcceptDeclineButtons(discord.ui.View):
    def __init__(self, user: discord.Member, callback):
        super().__init__(timeout=60)  # Timeout after 60 seconds
        self.user = user
        self.callback = callback
        self.value = None
        self.handled = False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = True
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has accepted the collaboration!",
                                                view=self)
        await self.callback(self.user, True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = False
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has declined the collaboration!",
                                                view=self)
        await self.callback(self.user, False)

    async def on_timeout(self):
        if not self.handled:
            self.disable_all_buttons()
            await self.message.edit(view=self)
            await self.callback(self.user, False)

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True
        self.handled = True


class LeaveTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="leave", aliases=["disband"], description="Leave your team", with_app_command=True)
    async def command(self, ctx):
        async with get_session() as session:
            pass
                
async def setup(bot):
    await bot.add_cog(LeaveTeam(bot))