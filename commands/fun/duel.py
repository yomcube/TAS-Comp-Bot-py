import discord
from discord.ext import commands
import asyncio
import random

class Connect4Duel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.columns = 7
        self.rows = 6
        self.board = [[' ' for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_player = 'X'
        self.game_over = False
        self.players = {}
        self.game_channel = None
        self.pending_challenges = {}
        self.move_timeout = 60  # Timeout in seconds
        self.timeout_task = None

    def reset_game(self):
        self.board = [[' ' for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_player = 'X'
        self.game_over = False
        self.players = {}
        self.game_channel = None

    def print_board(self):
        board_string = '```\n'
        emoji_map = {'X': '🔴', 'O': '🟡', ' ': '⚪️'}
        for row in self.board:
            board_string += ''.join(emoji_map[cell] for cell in row) + '\n'
        board_string += '```'
        return board_string

    def is_valid_location(self, col):
        return self.board[0][col] == ' '

    def get_next_open_row(self, col):
        for r in range(self.rows-1, -1, -1):
            if self.board[r][col] == ' ':
                return r

    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def winning_move(self, piece):
        # Check horizontal locations for win
        for c in range(self.columns - 3):
            for r in range(self.rows):
                if (self.board[r][c] == piece and self.board[r][c + 1] == piece and
                    self.board[r][c + 2] == piece and self.board[r][c + 3] == piece):
                    return True

        # Check vertical locations for win
        for c in range(self.columns):
            for r in range(self.rows - 3):
                if (self.board[r][c] == piece and self.board[r + 1][c] == piece and
                    self.board[r + 2][c] == piece and self.board[r + 3][c] == piece):
                    return True

        # Check positively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(self.rows - 3):
                if (self.board[r][c] == piece and self.board[r + 1][c + 1] == piece and
                    self.board[r + 2][c + 2] == piece and self.board[r + 3][c + 3] == piece):
                    return True

        # Check negatively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(3, self.rows):
                if (self.board[r][c] == piece and self.board[r - 1][c + 1] == piece and
                    self.board[r - 2][c + 2] == piece and self.board[r - 3][c + 3] == piece):
                    return True

        return False

    async def start_timer(self):
        await asyncio.sleep(self.move_timeout)
        if not self.game_over:
            self.game_over = True
            await self.game_channel.send("Time's up! The game has ended due to inactivity.")
            # Optionally, you can declare a winner based on who the current player is

    async def make_move(self, col, piece):
        if col < 0 or col >= self.columns:
            await self.game_channel.send("Invalid column! Please select a column between 1 and 7.")
            return

        if self.is_valid_location(col):
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, piece)
            if self.winning_move(piece):
                self.game_over = True
                await self.game_channel.send(self.print_board())
                winner = self.players[piece]
                await self.game_channel.send(f'Congratulations {winner.mention}, you won!')
            elif all(self.board[0][c] != ' ' for c in range(self.columns)):
                self.game_over = True
                await self.game_channel.send(self.print_board())
                await self.game_channel.send('The game is a tie!')
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                await self.game_channel.send(self.print_board())
                await self.game_channel.send(f'It\'s {self.players[self.current_player].mention}\'s turn!')

                # handle inactivity
                if self.timeout_task:
                    self.timeout_task.cancel()  # Cancel the existing timer task
                self.timeout_task = self.bot.loop.create_task(self.start_timer())  # Start a new timer task
        else:
            await self.game_channel.send(f'Column {col + 1} is full!')

    @commands.command()
    async def duel(self, ctx, opponent: discord.Member):
        if self.game_over or len(self.players) == 0:
            self.reset_game()
            self.players = {'X': ctx.author, 'O': opponent}
            self.game_channel = ctx.channel

            challenge_message = await ctx.send(
                f'{opponent.mention}, you have been challenged to a Connect 4 duel by {ctx.author.mention}! Type `$accept` to accept the challenge.')
            self.pending_challenges[opponent.id] = challenge_message
        else:
            await ctx.send('A game is already in progress. Finish that game before starting a new one!')

    @commands.command()
    async def accept(self, ctx):
        if ctx.author.id in self.pending_challenges:
            challenge_message = self.pending_challenges.pop(ctx.author.id)
            self.players['O'] = ctx.author
            self.game_channel = challenge_message.channel
            await self.game_channel.send(f'{ctx.author.mention} has accepted the challenge!')
            await self.start_game(ctx)
        else:
            await ctx.send('There is no pending challenge for you to accept.')

    async def start_game(self, ctx):
        self.timeout_task = self.bot.loop.create_task(self.start_timer())
        self.game_channel = ctx.channel
        random.shuffle(list(self.players.keys()))  # Randomize who starts
        await self.game_channel.send(
            f'Starting a new Connect 4 duel between {self.players["X"].mention} and {self.players["O"].mention}!')
        await self.game_channel.send(self.print_board())
        await self.game_channel.send(f'It\'s {self.players[self.current_player].mention}\'s turn!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot and not self.game_over and message.channel == self.game_channel:
            if message.author == self.players[self.current_player]:
                try:
                    col = int(message.content) - 1
                    await self.make_move(col, self.current_player)
                except ValueError:
                    pass  # Ignore non-integer messages

async def setup(bot):
    await bot.add_cog(Connect4Duel(bot))