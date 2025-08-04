# src/main.py

import asyncio
import os
import sys
import traceback

import discord
from discord.ext import commands
from dotenv import load_dotenv

from application.parsers.rkg_parser import RkgParser
from infrastructure.db import init_db
from infrastructure.repositories.sqlalchemy_task_repo import SqlAlchemyTaskRepository
from infrastructure.repositories.sqlalchemy_user_repo import SqlAlchemyUserRepository
from infrastructure.repositories.sqlalchemy_submission_repo import SqlAlchemySubmissionRepository
from infrastructure.repositories.sqlalchemy_team_repo import SqlAlchemyTeamRepository
from infrastructure.repositories.sqlalchemy_config_repo import SqlAlchemyConfigRepository
from infrastructure.repositories.sqlalchemy_speedtask_repo import SqlAlchemySpeedTaskRepository

from application.parsers.file_parser import FileParser
from application.services.task_manager import TaskManager
from application.services.submission_service import SubmissionService
from application.services.user_service import UserService
from application.services.team_service import TeamService
from application.services.config_service import ConfigService
from application.services.speed_task_service import SpeedTaskService


# ────────────────────────── ENV / TOKEN ────────────────────────────
load_dotenv()
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    print("❌TOKEN non défini dans .env", file=sys.stderr)
    sys.exit(1)

# ────────────────────────── BOT ACTIVITY ───────────────────────────
activity = discord.Game(name="Dolphin Emulator")

# ────────────────────────── EXTENSIONS -----------------------------
commands_ext = [
    "adapters.discord.commands.admin.config_commands",
    "adapters.discord.commands.admin.error_test_commands",
    "adapters.discord.commands.admin.sync_command",
    "adapters.discord.commands.admin.say_command",
    "adapters.discord.commands.comp.collab_command",
    "adapters.discord.commands.comp.leave_team_command",
    "adapters.discord.commands.comp.name_commands",
    "adapters.discord.commands.comp.request_task_command",
    "adapters.discord.commands.comp.stop_timer_command",
    "adapters.discord.commands.comp.teams_command",
    "adapters.discord.commands.host.delete_submission_command",
    "adapters.discord.commands.host.dm_command",
    "adapters.discord.commands.host.edit_submission_command",
    "adapters.discord.commands.host.end_task_command",
    "adapters.discord.commands.host.get_submissions_command",
    "adapters.discord.commands.host.host_dissolve_command",
    "adapters.discord.commands.host.set_deadline_command",
    "adapters.discord.commands.host.speed_task_config_commands",
    "adapters.discord.commands.host.start_task_command",
    "adapters.discord.commands.host.submit_command",



]

events_ext = [
    "adapters.discord.events.dm_logger",
    "adapters.discord.events.dm_submission_listener",
    "adapters.discord.events.discord_errors",
    "adapters.discord.events.deadline_watcher",
    "adapters.discord.events.speed_task_reminders",
    "adapters.discord.events.speed_task_release"
]

# ────────────────────────── BOT CLASS ──────────────────────────
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="$",
            intents=discord.Intents.all(),
            description="MKWii TAS Competition Bot",
            activity=activity,
        )

    async def setup_hook(self):
        # load commands
        for ext in commands_ext:
            try:
                await self.load_extension(ext)
            except Exception:
                print(f"Loading fail {ext}", file=sys.stderr)
                traceback.print_exc()

        # load listeners and events
        for ext in events_ext:
            try:
                await self.load_extension(ext)
            except Exception:
                print(f"Loading fail {ext}", file=sys.stderr)
                traceback.print_exc()


# ────────────────────────── MAIN ──────────────────────────
def main() -> None:
    # 1) init database
    asyncio.run(init_db())

    # 2) Instanciate the bot
    bot = Bot()



    # 3) repositories
    user_repo = SqlAlchemyUserRepository()
    task_repo = SqlAlchemyTaskRepository()
    team_repo = SqlAlchemyTeamRepository(user_repo=user_repo)
    submission_repo = SqlAlchemySubmissionRepository(
        user_repo=user_repo,
        task_repo=task_repo,
        team_repo=team_repo,
    )
    config_repo = SqlAlchemyConfigRepository()
    speed_repo  = SqlAlchemySpeedTaskRepository(user_repo=user_repo, task_repo=task_repo)

    # 4) Services and parsers
    file_parser       = FileParser(RkgParser) # TODO: Create default parser that does nothing, and pass that as default
    config_service    = ConfigService(config_repo)
    user_service      = UserService(user_repo, bot)


    task_manager = TaskManager(
        task_repo=task_repo,
        config_service=config_service,
        submission_repo=submission_repo,
        team_repo=team_repo,
        speed_repo=speed_repo
    )

    submission_service = SubmissionService(
        user_svc=user_service,
        submission_repo=submission_repo,
        task_repo=task_repo,
        user_repo=user_repo,
        file_parser=file_parser,
        team_repo=team_repo,
        speed_repo=speed_repo
    )

    team_service = TeamService(
        user_svc=user_service,
        team_repo=team_repo,
        user_repo=user_repo,
        task_repo=task_repo
    )
    speed_task_service = SpeedTaskService(
        speed_repo=speed_repo,
        task_repo=task_repo,
        user_svc=user_service,
        cfg_svc=config_service
    )

    # 5) Inject services into the bot as attributes
    bot.task_manager        = task_manager
    bot.config_service      = config_service
    bot.submission_service  = submission_service
    bot.speed_task_service  = speed_task_service
    bot.team_service        = team_service
    bot.user_service        = user_service

    # 6) run
    bot.remove_command("help")
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
