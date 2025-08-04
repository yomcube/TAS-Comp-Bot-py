"""
Start Task Command
==================

Module path:
    src/adapters/discord/commands/host/start_task_command.py

Summary:
    Hybrid command that starts a new competition (and marks it as active) with the
    parameters provided by a Host. Validates inputs with Pydantic, ensures
    required speed-task configuration is present when applicable, resets
    competition tables, clears the submitter role from members,
    and cleans up the previous “Current Submissions” message.

Responsibilities:
    - Enforce host-only access (via `@host_only()` check).
    - Validate task parameters (`TaskConfig`).
    - For speed-tasks, ensure required config entries exist (desc/length/reminders).
    - Start the task via `TaskManager.start_task(...)` (which resets related tables).
    - Clear submitter role from everyone in the guild.
    - Remove any previous “Current Submissions” bot message.
"""

import time
import traceback
from typing import Optional

import discord
from discord.ext import commands
from pydantic import ValidationError

from adapters.discord.checks import host_only
from adapters.discord.utils.role_utils import clear_role_for_guild
from application.models import TaskConfig
from application.services.task_manager import TaskManager
from application.services.config_service import ConfigService


class StartTaskCommand(commands.Cog):
    """
    Start a competition (and setting `is_active=True`). Host-only.

    Hybrid usage:
        $start-task <number> <year?> <team_size?> <multiple_tracks?> <speed_task?> <deadline>
        /start-task   (same arguments via slash)

    Attributes:
        task_manager (TaskManager): Application service orchestrating task lifecycle.
        cfg_svc (ConfigService): Service to read competition/guild configuration.
    """

    def __init__(
        self,
        task_manager: TaskManager,
        config_service: ConfigService,
    ):
        self.task_manager = task_manager
        self.cfg_svc      = config_service

    @commands.hybrid_command(
        name="start-task",
        description="[Host] Start a new task",
        with_app_command=True
    )
    @host_only()
    async def start_task(
        self,
        ctx: commands.Context,
        number: int,
        *,
        year: Optional[int] = None,
        team_size: int = 1,
        multiple_tracks: bool = False,
        speed_task: bool = False,
        deadline: int,
    ):
        """
        Open a new competition with the provided parameters.

        Flow:
            1) If `speed_task` is True, verify required speed-task config exists
               (description, length, at least the first reminder).
            2) Validate parameters using `TaskConfig` (Pydantic).
            3) Ensure `deadline` is in the future.
            4) Start the task via `TaskManager.start_task` (which performs table resets).
            5) Clear the submitter role from all members in the guild (fresh season).
            6) Confirmation message.
            7) Remove the previous “Current Submissions” message if present.

        Args:
            ctx (commands.Context): Invocation context.
            number (int): Task number (competition identifier).
            year (Optional[int]): Year (defaults via Pydantic validator if omitted).
            team_size (int): Maximum players per team (1 for solo).
            multiple_tracks (bool): If True, `.rksys` files are enforced; else `.rkg`.
            speed_task (bool): If True, task starts hidden and will be released later.
            deadline (int): Absolute deadline (UNIX epoch seconds).

        Returns:
            None
        """
        # 1) For speed-tasks, ensure necessary configuration is present
        if speed_task:
            gc = await self.cfg_svc.get_guild_config(ctx.guild.id)
            if not gc:
                return await ctx.send("There is no competition configured for this server. Use `/set-comp`.")
            comp = gc.comp

            desc_cfg   = await self.cfg_svc.get_speed_task_desc(comp)
            length_cfg = await self.cfg_svc.get_speed_task_length(comp)
            remind_cfg = await self.cfg_svc.get_speed_task_reminders(comp)

            missing = []
            if not desc_cfg or not desc_cfg.desc.strip():
                missing.append("description")
            if not length_cfg or length_cfg.time <= 0:
                missing.append("length")
            # require at least the first reminder
            if not remind_cfg or remind_cfg.reminder1 is None:
                missing.append("reminders")

            if missing:
                return await ctx.send(
                    "Couldn't start the speed task; "
                    f"missing or invalid configuration for: {', '.join(missing)}."
                )

        # 2) Validate parameters using Pydantic DTO
        try:
            cfg = TaskConfig(
                number=number,
                year=year,
                team_size=team_size,
                multiple_tracks=multiple_tracks,
                speed_task=speed_task,
                deadline=deadline,
            )
        except ValidationError as e:
            return await ctx.send(f"Invalid task parameters {e}")

        # 3) Deadline must be in the future
        now = int(time.time())
        if cfg.deadline <= now:
            return await ctx.send("This deadline is in the past! Please use a deadline in the future :P")

        # 4) Start the competition (resets related tables inside TaskManager)
        try:
            task = await self.task_manager.start_task(cfg)
        except Exception as exc:
            # Printing for debugging
            traceback.print_exc()
            return await ctx.send(f"Ran into a problem that prevent task from being started: {exc}")

        # 5) Clear the submitted role from all members
        guild_cfg = await self.cfg_svc.get_guild_config(ctx.guild.id)
        if guild_cfg:
            submit_cfg = await self.cfg_svc.get_submitter_role(guild_cfg.comp)
            if submit_cfg and submit_cfg.role_id:
                await clear_role_for_guild(ctx.guild, submit_cfg.role_id)

        # 6) Confirmation message with formatted deadline
        await ctx.send(
            f"Successfully started **Task {task.number}, {task.year}**! "
            f"Deadline: <t:{task.deadline}:F>."
        )

        # 7) Clean up the previous “Current Submissions” message (if any)
        return await self._delete_previous_submission_msg(ctx)

    async def _delete_previous_submission_msg(self, ctx: commands.Context) -> None:
        """
        Search and delete the last bot message in the configured submissions channel.

        Args:
            ctx (commands.Context): Invocation context (to resolve guild/channels).

        Returns:
            None
        """
        gc = await self.cfg_svc.get_guild_config(ctx.guild.id)
        if not gc:
            return
        sub_ch_cfg = await self.cfg_svc.get_submission_channel(gc.comp)
        if not sub_ch_cfg:
            return

        channel = ctx.guild.get_channel(sub_ch_cfg.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        # Scan the past 5 messages
        async for msg in channel.history(limit=5):
            if msg.author == ctx.bot.user:
                try:
                    await msg.delete()
                except discord.HTTPException:
                    pass
                break


async def setup(bot: commands.Bot) -> None:
    """
    Register the StartTaskCommand cog with the bot.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(
        StartTaskCommand(
            task_manager=  bot.task_manager,
            config_service=bot.config_service,
        )
    )
