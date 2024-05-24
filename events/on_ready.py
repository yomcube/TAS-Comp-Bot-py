from discord.ext import commands
import sqlite3

class Ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        # Database for tasks and submissions
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
                                time TEXT,
                                dq INTEGER
                                )""") # dq is boolean: 0 or 1
        connection.commit()
        connection.close()
        
        
        # Database for economy commands
        connection = sqlite3.connect("database/economy.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS slots (
                                username TEXT, 
                                coins INTEGER
                                )""")
        connection.commit()
        connection.close()

        print('Bot is ready!')



async def setup(bot):
    await bot.add_cog(Ready(bot))
