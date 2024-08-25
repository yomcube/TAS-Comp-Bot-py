import discord
from discord.ext import commands
from api import submissions


class Message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):

        # Reacting to new members joining
        if message.guild is not None and message.channel.id == message.guild.system_channel.id:
            if message.type == discord.MessageType.new_member:
                emoji = "👀"
                await message.add_reaction(emoji)

        await submissions.handle_dms(message, self)

        content = message.content
        lower_content = content.lower()

        msg_list = ["kierio", "crazy", "😃", "when stream"]

        if str(lower_content).startswith(msg_list[0]):
            await message.reply("kiro*")
        elif (str(lower_content).startswith(msg_list[1]) or str(lower_content).endswith(msg_list[1])):
            await message.reply("Crazy?")
            await self.wait_crazy(message)
        elif msg_list[2] in lower_content:
            await message.add_reaction("✈️")
        elif msg_list[3] in lower_content:
            await message.reply(
                "The stream will start at <t:1721689200:t> (local time), unless said otherwise by streamer or the host.")


    async def wait_crazy(self, message):
        def check(m):
            return m.author == message.author and m.channel == message.channel

        crazy_list = ["i was crazy once", "a rubber room", "and rats make me crazy"]
        response = await self.bot.wait_for('message', check=check)
        response_lower = response.content.lower()
        if response_lower.startswith(crazy_list[0]):
            await response.reply("They locked me in a room.")
            response = await self.bot.wait_for('message', check=check)
            response_lower = response.content.lower()
            if response_lower.startswith(crazy_list[1]):
                await response.reply("A rubber room with rats.")


async def setup(bot):
    await bot.add_cog(Message(bot))