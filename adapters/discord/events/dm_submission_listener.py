"""
DM Submission Listener
======================

Module path:
    src/adapters/discord/events/dm_submission_listener.py

Summary:
    Cog that listens for direct messages (DMs) sent to the bot
    and processes valid competition submissions.

Responsibilities:
    - Validate file type based on general allowed extensions and
      competition-specific settings.
    - Check active competition and speed-task sessions when required.
    - Delegate the actual submission creation to SubmissionService.
    - Refresh the public submissions list.
    - Assign the "submitted" role to users (except in speed-tasks).
"""

from typing import Optional

import discord
from discord.ext import commands

from adapters.discord.utils.role_utils import add_role_to_member
from adapters.discord.utils.submission_utils import refresh_submission_list
from application.services.submission_service import SubmissionService
from application.services.speed_task_service    import SpeedTaskService
from application.services.task_manager          import TaskManager
from application.services.config_service        import ConfigService

# Accepted extensions in general
VALID_EXT = (".rkg", ".rksys")


class DMSubmissionListener(commands.Cog):
    """
    Cog that processes competition submissions sent via DMs to the bot.

    Workflow:
        1. Validates the attachment file type.
        2. Verifies the active competition and any speed-task session.
        3. Submits the file using SubmissionService.
        4. Updates the public submissions list.
        5. Assigns the "submitted" role (non-speed tasks only).
    """

    bot: commands.Bot  # Will be set in setup()

    def __init__(
        self,
        submission_service: SubmissionService,
        speed_svc:          SpeedTaskService,
        task_mgr:           TaskManager,
        config_service:     ConfigService,
    ):
        """
        Initialize the listener.

        Args:
            submission_service (SubmissionService): Service handling submissions.
            speed_svc (SpeedTaskService): Service managing speed-task sessions.
            task_mgr (TaskManager): Service managing competitions/tasks.
            config_service (ConfigService): Service for retrieving configuration.
        """
        self.sub_svc   = submission_service
        self.speed_svc = speed_svc
        self.task_mgr  = task_mgr
        self.cfg_svc   = config_service

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """
        Event listener that processes DMs with attachments as submissions.

        Args:
            msg (discord.Message): Incoming message object.
        """
        # 0) Ignore bots, guild messages, or messages without attachments
        if msg.author.bot or msg.guild is not None or not msg.attachments:
            return

        fn = msg.attachments[0].filename.lower()

        # 1) Check general file extension validity
        if not fn.endswith(VALID_EXT):
            return await msg.channel.send("Unrecognized file type (must be .rkg or .rksys to submit).")

        # 2) Check active competition
        task = await self.task_mgr.get_active_task()
        if not task:
            return await msg.channel.send("There is no ongoing task!")

        # 3) Enforce competition-specific file type
        #    multiple_tracks=False → only .rkg allowed
        #    multiple_tracks=True  → only .rksys allowed
        if not task.multiple_tracks and not fn.endswith(".rkg"):
            return await msg.channel.send("This task only accepts .rkg files.")
        if task.multiple_tracks and not fn.endswith(".rksys"):
            return await msg.channel.send("This task only accepts .rksys files.")

        # 4) If speed-task, verify user's session
        if task.speed_task:
            session = await self.speed_svc.get_session_for_user(msg.author.id)
            if not session:
                return await msg.channel.send(
                    "You may not submit to this speed task as of now! Use `$requesttask` first."
                )
            if not session.is_active():
                return await msg.channel.send("Your speed task is already over! You cannot submit.")

        # 5) Read file bytes and URL
        file_bytes = await msg.attachments[0].read()
        file_url   = msg.attachments[0].url

        # 6) Submit via SubmissionService
        try:
            submission = await self.sub_svc.submit(
                user_id    = msg.author.id,
                file_bytes = file_bytes,
                file_url   = file_url,
            )
        except Exception as exc:
            return await msg.channel.send(f"Submission failed: {exc}")

        # 7) Resolve the server/guild configured for this bot
        target_guild: Optional[discord.Guild] = self.bot.guilds[0] if self.bot.guilds else None
        if target_guild:
            # Ensure the guild is actually configured for the competition
            gc = await self.cfg_svc.get_guild_config(target_guild.id)
            if not gc:
                target_guild = None

        # 8) Refresh submission list
        if target_guild:
            await refresh_submission_list(
                bot    = self.bot,
                cfg_svc= self.cfg_svc,
                sub_svc= self.sub_svc,
                guild  = target_guild,
            )

        # 9) Assign submitted role if not a speed-task
        if target_guild and not task.speed_task:
            gc         = await self.cfg_svc.get_guild_config(target_guild.id)
            submit_cfg = await self.cfg_svc.get_submitter_role(gc.comp)
            if submit_cfg and submit_cfg.role_id:
                if submission.team:
                    for u in submission.team.members:
                        await add_role_to_member(target_guild, u.discord_id, submit_cfg.role_id)
                else:
                    await add_role_to_member(target_guild, msg.author.id, submit_cfg.role_id)

        # 10) Confirm submission to the user
        extension = (msg.attachments[0].filename.lower().split("."))[1]
        return await msg.channel.send(f"`.{extension}` file detected!\n"
                                            f"The file was successfully saved. Type `$info` for more information "
                                            f"about the file."
                                      )


async def setup(bot: commands.Bot):
    """
    Setup function to add this Cog to the bot.

    Args:
        bot (commands.Bot): The Discord bot instance.
    """
    cog = DMSubmissionListener(
        submission_service=bot.submission_service,
        speed_svc=         bot.speed_task_service,
        task_mgr=          bot.task_manager,
        config_service=    bot.config_service,
    )
    cog.bot = bot  # type: ignore
    await bot.add_cog(cog)
