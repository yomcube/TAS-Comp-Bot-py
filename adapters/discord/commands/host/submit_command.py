"""
Host Submit Command
===================

Module path:
    src/adapters/discord/commands/host/submit_command.py

Summary:
    Command that lets a Host submit a file on behalf of a user.
    It validates the file type against current competition
    settings, delegates persistence to the SubmissionService, refreshes the
    public submissions list, and assigns the "submitter" role when applicable.


Responsibilities:
    - Enforce host-only access (via `@host_only()` check).
    - Validate that a competition is configured and currently active.
    - Enforce allowed file extension depending on `task.multiple_tracks`.
    - Call `SubmissionService.submit(...)` to parse & store the submission.
    - Refresh the public "Current Submissions" message.
    - Assign the submitter role to the solo user or to all team members.
"""

import discord
from discord.ext import commands

from adapters.discord.checks import host_only
from adapters.discord.utils.submission_utils import refresh_submission_list
from adapters.discord.utils.role_utils import add_role_to_member
from application.services.submission_service import SubmissionService
from application.services.config_service     import ConfigService
from application.services.task_manager       import TaskManager


class SubmitCommand(commands.Cog):
    """
    `/submit @user <file>` — Host-only.

    Allows a Host to submit a file for a given user.
    After a successful submission, the submissionlist is
    refreshed and the submitter role is granted.

    Attributes:
        sub_svc (SubmissionService): Application service handling submissions.
        cfg_svc (ConfigService): Service to access competition/guild config.
        task_mgr (TaskManager): Service to query the active task.
    """

    def __init__(
        self,
        submission_svc: SubmissionService,
        config_svc:     ConfigService,
        task_mgr:       TaskManager,
    ):
        self.sub_svc  = submission_svc
        self.cfg_svc  = config_svc
        self.task_mgr = task_mgr

    @commands.hybrid_command(
        name="submit",
        description="[Host] Submit a file on behalf of a competitor.",
        with_app_command=True,
    )
    @host_only()
    async def submit(
        self,
        ctx:    commands.Context,
        member: discord.Member,
        file:   discord.Attachment,
    ):
        """
        Submit a submission file on behalf of `member`.

        Flow:
            1) Ensure the server is configured for a competition.
            2) Ensure an active competition exists.
            3) Enforce the allowed extension based on `multiple_tracks`.
            4) Read file bytes and call `SubmissionService.submit(...)`.
            5) Refresh the public submissions list message.
            6) Assign the submitter role (solo or team) if configured.
            7) Confirm to the Host with the parsed time and file URL.

        Args:
            ctx (commands.Context): Invocation context.
            member (discord.Member): Target user for whom we submit.
            file (discord.Attachment): The uploaded `.rkg` or `.rksys` file.

        Returns:
            None
        """
        # 1) Guild/competition configured?
        gc = await self.cfg_svc.get_guild_config(ctx.guild.id)
        if not gc:
            return await ctx.send("There is no competition configured for this server. Use `/set-comp`.")

        # 2) Active competition?
        task = await self.task_mgr.get_active_task()
        if not task:
            return await ctx.send("There is no active task!")

        # 3) Extension check based on single-track / multi-track rules
        fname = file.filename.lower()
        if task.multiple_tracks:
            if not fname.endswith(".rksys"):
                return await ctx.send("This task is for multiple tracks; please submit an `.rksys` file.")
        else:
            if not fname.endswith(".rkg"):
                return await ctx.send("This task is for a single track; please submit an `.rkg` file.")

        # 4) Read file bytes & delegate to the submission service
        data = await file.read()
        try:
            submission = await self.sub_svc.submit(
                user_id=member.id,
                file_bytes=data,
                file_url=file.url,
            )
        except Exception as exc:
            # Print out the exception for debugging
            return await ctx.send(f"Couldn't submit : {exc}")

        # 5) Refresh the public submission list
        await refresh_submission_list(
            bot=    ctx.bot,
            cfg_svc=self.cfg_svc,
            sub_svc=self.sub_svc,
            guild=  ctx.guild,
        )

        # 6) Assign the submitter role (team: all members; solo: just the user)
        guild_cfg   = await self.cfg_svc.get_guild_config(ctx.guild.id)
        submit_cfg  = await self.cfg_svc.get_submitter_role(guild_cfg.comp)

        if submit_cfg and submit_cfg.role_id:
            if submission.team:
                # Team submission → grant to all teammates
                for user in submission.team.members:
                    await add_role_to_member(ctx.guild, user.discord_id, submit_cfg.role_id)
            else:
                # Solo submission → grant to the member only
                await add_role_to_member(ctx.guild, member.id, submit_cfg.role_id)

        # 7) Confirmation message with formatted time and URL
        secs = submission.time
        mins = int(secs // 60)
        rem  = secs - mins * 60
        timestamp = f"{mins}:{rem:06.3f}"
        await ctx.send(
            f"Succesfully submitted for {member.mention}: **{timestamp}**\n{file.url}"
        )


async def setup(bot: commands.Bot):
    """
    Register the `SubmitCommand` cog.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(
        SubmitCommand(
            submission_svc=bot.submission_service,
            config_svc=bot.config_service,
            task_mgr=bot.task_manager,
        )
    )
