import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from api.utils import get_team_size, is_in_team
from api.db_classes import Teams, Userbase, get_session
from api.submissions import new_competitor, get_display_name, get_seeking_channel
from sqlalchemy import select, insert, update, delete
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class AcceptDeclineButtons(discord.ui.View):
    def __init__(self, user: discord.Member, inviter: discord.Member, callback, cancel_callback):
        super().__init__(timeout=43200)  # Timeout after 12 hours
        self.user = user
        self.inviter = inviter
        self.callback = callback
        self.cancel_callback = cancel_callback
        self.value = None
        self.handled = False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = True
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has accepted the collaboration!", view=self)
        await self.callback(self.user, True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = False
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has declined the collaboration!", view=self)
        await self.callback(self.user, False)


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.inviter:
            await interaction.response.send_message("Only the person who sent the invite can cancel it!",
                                                    ephemeral=True)
            return
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"The collaboration invite to <@{self.user.id}> has been canceled.", view=self)
        await self.cancel_callback(self.user, interaction.user)  # Pass the user who was invited and who cancelled

    async def on_timeout(self):
        if not self.handled:
            self.disable_all_buttons()
            await self.message.edit(content=f"The collaboration request to <@{self.user.id}> has timed out.", view=self)
            await self.callback(self.user, False)

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True
        self.handled = True


class Collab(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_collabs = {}  # Track pending collaborations per author


    @commands.hybrid_command(name="collab", description="Collaborate with someone during a team task", with_app_command=True)
    async def collab(self, ctx, users: Greedy[discord.Member]):
        author_id = ctx.author.id

        # Check if the author already has a pending collaboration
        if author_id in self.pending_collabs:
            return await ctx.send("You already have a pending collaboration request. Please wait for it to be resolved, or cancel it.")

        team_size = await get_team_size()

        #####################
        # Case handling
        #####################

        # Is there a task running?
        if team_size is None:
            return await ctx.send("There is no task running currently.")

        # Verify if it's indeed a collab task
        elif team_size < 2:
            return await ctx.send("This is a solo task. You may **not** collaborate!")

        # Check for invalid users
        if not users:
            return await ctx.send("You didn't specify any valid members!")

        # Check if invited person is already in a team
        for user in users:
            if await is_in_team(user.id):
                return await ctx.send(f"{user.display_name} is already in a team and cannot join another.",
                    allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)

        # Check if the author is already in a team
        current_team = await self.get_current_team(author_id)

        # Check if adding new users exceeds the team size limit
        if current_team:
            if len(current_team) + len(users) > team_size:
                return await ctx.send("You are trying to exceed the team size limit!")
            else:
                await ctx.send("Inviting new members to your existing team...")

        # Make sure they don't try to collab with too many people (if not already in a team)
        elif len(users) + 1 > team_size:
            return await ctx.send("You are trying to collab with too many people!")

        # Make sure they are not collaborating with themselves: absurd
        for user in users:
            if user.id == author_id:
                return await ctx.send("Collaborating with... yourself? sus")




        #####################
        # Button view
        #####################

        pending_users = {user.id: None for user in users}
        self.pending_collabs[author_id] = pending_users

        for user in users:
            view = AcceptDeclineButtons(
                user, ctx.author,
                lambda u, a: self.user_response(ctx, author_id, u, a),
                lambda u, cu: self.cancel_collab(ctx, author_id, u, cu)  # Ensure correct parameters are being passed
            )
            message = await ctx.send(
                f"{user.mention}, {ctx.author.display_name} wants you to collaborate with them. Do you accept?",
                view=view, allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True
            )
            view.message = message  # Store the message in the view for later editing

        ####################################
        # Adding executor to user db if new
        ####################################
        if await new_competitor(ctx.author.id):
            async with get_session() as session:
                await session.execute(
                    insert(Userbase).values(
                        user_id=ctx.author.id,
                        user=self.bot.get_user(ctx.author.id).name,
                        display_name=self.bot.get_user(ctx.author.id).display_name
                    )
                )
                await session.commit()

    async def get_current_team(self, user_id):
        async with get_session() as session:
            result = await session.execute(
                select(Teams).where(
                    (Teams.leader == user_id) |
                    (Teams.user2 == user_id) |
                    (Teams.user3 == user_id) |
                    (Teams.user4 == user_id)
                )
            )
            team = result.scalar()
            if team:
                team_members = [team.leader, team.user2, team.user3, team.user4]
                return [member for member in team_members if member]
            return None

    async def user_response(self, ctx, author_id, user, accepted):
        if author_id in self.pending_collabs and user.id in self.pending_collabs[author_id]:
            self.pending_collabs[author_id][user.id] = accepted

            # Check if all responses are in
            if all(response is not None for response in self.pending_collabs[author_id].values()):
                accepted_users = [uid for uid, resp in self.pending_collabs[author_id].items() if resp]

                if accepted_users:
                    # Fetch the current team
                    current_team = await self.get_current_team(author_id)

                    if current_team:
                        # Prepare the list of new members before modifying
                        async with get_session() as session:
                            team_info = await session.execute(
                                select(Teams).where(
                                    (Teams.leader == author_id) |
                                    (Teams.user2 == author_id) |
                                    (Teams.user3 == author_id) |
                                    (Teams.user4 == author_id)
                                )
                            )
                            team_info = team_info.scalar_one_or_none()

                            if team_info:
                                current_team_ids = [team_info.leader, team_info.user2, team_info.user3, team_info.user4]
                                new_members = [uid for uid in accepted_users if uid not in current_team_ids]

                                updates = {}
                                if not team_info.user2 and new_members:
                                    updates['user2'] = new_members.pop(0)
                                if not team_info.user3 and new_members:
                                    updates['user3'] = new_members.pop(0)
                                if not team_info.user4 and new_members:
                                    updates['user4'] = new_members.pop(0)

                                if updates:
                                    # Update the team in the database
                                    await session.execute(
                                        update(Teams).where(
                                            (Teams.leader == team_info.leader) &
                                            (Teams.user2 == team_info.user2) &
                                            (Teams.user3 == team_info.user3) &
                                            (Teams.user4 == team_info.user4)
                                        ).values(**updates)
                                    )

                                    # Commit changes to the session
                                    await session.commit()

                                # Prepare the mentions before popping elements from new_members
                                new_member_mentions = ", ".join(
                                    f"<@{uid}>" for uid in [updates[key] for key in updates])

                                if new_member_mentions:
                                    await ctx.send(f"{new_member_mentions} has been added to your team!")
                                else:
                                    await ctx.send("Nobody has been added to your team as all invitations were declined, cancelled, or timed out")

                    else:
                        # No existing team, create a new team
                        user_mentions = ", ".join(f"<@{uid}>" for uid in accepted_users if uid != author_id)
                        async with get_session() as session:
                            await session.execute(
                                insert(Teams).values(
                                    team_name=" & ".join(
                                        [self.bot.get_user(uid).display_name for uid in [author_id] + accepted_users]),
                                    leader=author_id,
                                    user2=accepted_users[0] if len(accepted_users) > 0 else None,
                                    user3=accepted_users[1] if len(accepted_users) > 1 else None,
                                    user4=accepted_users[2] if len(accepted_users) > 2 else None
                                )
                            )

                            # Add any new users to Userbase db
                            for id in accepted_users:
                                if await new_competitor(id):
                                    await session.execute(
                                        insert(Userbase).values(
                                            user_id=id,
                                            user=self.bot.get_user(id).name,
                                            display_name=self.bot.get_user(id).display_name
                                        )
                                    )

                            await session.commit()

                        await ctx.send(f"<@{author_id}> is now collaborating with {user_mentions}!")

                    del self.pending_collabs[author_id]

                else:
                    if await is_in_team(author_id):
                        message = "Nobody has been added to your team as all invitations were declined, cancelled, or timed out"
                    else:
                        message = "No team was formed as all invitations were declined, cancelled or timed out."

                    await ctx.send(message)
                    del self.pending_collabs[author_id]



    async def cancel_collab(self, ctx, author_id, invited_user, cancelling_user):
            if author_id in self.pending_collabs and invited_user.id in self.pending_collabs[author_id]:
                self.pending_collabs[author_id][invited_user.id] = False  # Treat cancellation as a decline


                # Check if this cancellation resolves the pending state
                if all(resp is not None for resp in self.pending_collabs[author_id].values()):
                    accepted_users = [uid for uid, resp in self.pending_collabs[author_id].items() if resp]
                    if accepted_users:
                        user_mentions = ", ".join(f"<@{uid}>" for uid in accepted_users)
                        await ctx.send(f"<@{author_id}> is now collaborating with {user_mentions}!")

                        members = []
                        members.append(await get_display_name(author_id))

                        for member in accepted_users:
                            if await get_display_name(member) is not None:
                                member_name = await get_display_name(member)
                            else:
                                member_name = self.bot.get_user(member).display_name
                            members.append(member_name)
                        default_team_name = " & ".join(members)

                        # Add team to Teams db
                        async with get_session() as session:
                            await session.execute(
                                insert(Teams).values(
                                    team_name=default_team_name,
                                    leader=author_id,
                                    user2=accepted_users[0] if len(accepted_users) > 0 else None,
                                    user3=accepted_users[1] if len(accepted_users) > 1 else None,
                                    user4=accepted_users[2] if len(accepted_users) > 2 else None
                                )
                            )

                            # Add any new users to Userbase db
                            for id in accepted_users:
                                if await new_competitor(id):
                                    await session.execute(
                                        insert(Userbase).values(
                                            user_id=id,
                                            user=self.bot.get_user(id).name,
                                            display_name=self.bot.get_user(id).display_name
                                        )
                                    )
                            await session.commit()

                        del self.pending_collabs[author_id]  # Clear the collaboration state
                    else:
                        if await is_in_team(author_id):
                            message = "Nobody has been added to your team as all invitations were declined, cancelled, or timed out"
                        else:
                            message = "No team was formed as all invitations were declined, cancelled or timed out."

                        await ctx.send(message)
                        del self.pending_collabs[author_id]  # Clear the collaboration state


async def setup(bot):
    await bot.add_cog(Collab(bot))