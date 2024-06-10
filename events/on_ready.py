from discord.ext import commands
import sqlite3

host_role_id = None


class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        '''# Database for tasks and submissions
        connection = sqlite3.connect("database/tasks.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                                task INTEGER,
                                year INTEGER,
                                is_active INTEGER,
                                collab INTEGER,
                                multiple_tracks INTEGER,
                                speed_task INTEGER
                                )""")  # the collab value should be interpreted as collab with X other player (1 would imply 2 people, 2 would imply 3 people)
                                        # multiple_tracks and speed_task are booleans: 0 or 1
        cursor.execute("""CREATE TABLE IF NOT EXISTS submissions (
                                task INTEGER,
                                name TEXT,
                                id INTEGER,
                                url TEXT,
                                time FLOAT,
                                dq INTEGER,
                                dq_reason TEXT
                                )""") # dq is boolean: 0 or 1. Time is counted in SECONDS
        connection.commit()
        connection.close()


        # Database for economy commands
        connection = sqlite3.connect("database/economy.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS money (
                                username TEXT,
                                coins INTEGER
                                )""")
        connection.commit()
        connection.close()


        # Database for settings
        connection = sqlite3.connect("database/settings.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS submission_channel (
                                        comp TEXT,
                                        id INTEGER
                                        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS host_role (
                                        comp TEXT,
                                        name TEXT,
                                        id INTEGER
                                        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS logs_channel (
                                                comp TEXT,
                                                id INTEGER
                                                )""")


        connection.commit()
        connection.close()

        # Database for users -> user (handle), id, display_name (used for submission list)
        connection = sqlite3.connect("database/users.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS userbase (
                                                user TEXT,
                                                id INTEGER,
                                                display_name TEXT
                                                )""")

        # TODO: flag can_change_name; if it's 0, user is locked from changing their name

        connection.commit()
        connection.close()
        '''

        print('Bot is ready!')


async def setup(bot):
    await bot.add_cog(Ready(bot))
