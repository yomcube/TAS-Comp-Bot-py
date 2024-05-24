from discord.ext import commands
import random
import sqlite3
import discord

class Slots(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    def get_balance(self, username):
        connection = sqlite3.connect("database/economy.db")
        cursor = connection.cursor()
        cursor.execute("SELECT coins FROM slots WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO slots (username, coins) VALUES (?, ?)", (username, 100))
            connection.commit()
            balance = 100
        else:
            balance = result[0]
        connection.close()
        return balance

    def update_balance(self, username, new_balance):
        connection = sqlite3.connect("database/economy.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE slots SET coins = ? WHERE username = ?", (new_balance, username))
        connection.commit()
        connection.close()

    def add_balance(self, username, amount):
        current_balance = self.get_balance(username)
        new_balance = current_balance + amount
        self.update_balance(username, new_balance)

    def deduct_balance(self, username, amount):
        current_balance = self.get_balance(username)
        new_balance = max(current_balance - amount, 0)  # Ensure balance doesn't go negative
        self.update_balance(username, new_balance)

    def calculate_winnings(self, num_emojis, slot_number, base_amount=10):
        probability = 1 / (num_emojis ** slot_number)
        winnings = base_amount * (1 / probability)
        return int(winnings)

    @commands.hybrid_command(name="slots", description="Slots through server emojis", with_app_command=True)
    async def command(self, ctx, number: int = 3):
        username = ctx.author.name
        cost_per_play = 5

        if self.get_balance(username) < cost_per_play:
            await ctx.reply("You don't have enough coins to play.")
            return

        self.deduct_balance(username, cost_per_play)

        emojis = ctx.message.guild.emojis
        emojis_list = [str(emoji) for emoji in emojis]
        random_emojis = random.choices(emojis_list, k=number)
        result = " ".join(random_emojis)
        play_again_text = f"Please Play Again\n{self.get_balance(username)} coins left in your account"
        
        while len(result) > 2000:
            random_emojis.pop()
            result = " ".join(random_emojis)
            play_again_text = f"*(message above was truncated since {number} exceeds the max length of 2000 characters)*\nPlease Play Again\n{self.get_balance(username)} coins left in your account."
            
        if number <= 0:
            await ctx.reply("What did you think would happen uh?")
            return
        else:
            await ctx.reply(result)
        
        if number == 1:
            await ctx.send("You won! wait...")
        elif all(emoji == random_emojis[0] for emoji in random_emojis):
            probability = 1 / (len(emojis_list) ** number)
            percentage = probability * 100
            winnings = self.calculate_winnings(len(emojis_list), number)
            self.add_balance(username, winnings)
            await ctx.send(f"You won! The probability of winning was {percentage:.2f}% (1 in {int(1/probability)}).\n{winnings} coins were added to your balance. {self.get_balance(username)} coins left in your account.")
        else:
            await ctx.send(play_again_text)

    @commands.hybrid_command(name="balance", description="Check your balance.", with_app_command=True)
    async def balance(self, ctx, user: discord.Member=None):
        if user:
            balance = self.get_balance(user)
            await ctx.reply(f"{user.display_name} current balance is {balance} coins.")
        else:
            username = ctx.author.name
            balance = self.get_balance(username)
            await ctx.reply(f"Your current balance is {balance} coins.")

    @commands.hybrid_command(name="addcoins", description="Add coins to user's balances (admin only)", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def addcoins(self, ctx, user: discord.Member, amount: int):
        username = user.name
        self.add_balance(username, amount)
        await ctx.reply(f"Added {amount} coins to {user.display_name}'s balance.")

async def setup(bot) -> None:
    await bot.add_cog(Slots(bot))
