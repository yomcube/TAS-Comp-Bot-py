import discord
from discord.ext import commands
from discord import app_commands
import typing
import random

class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.columns = 7
        self.rows = 6
        self.board = [[' ' for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_player = 'X'
        self.game_over = False
        self.mode = "easy"

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

    async def make_move(self, ctx, col, piece):
        if self.is_valid_location(col):
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, piece)
            if self.winning_move(piece):
                self.game_over = True
                await ctx.send(self.print_board())
                if piece == 'X':
                    await ctx.send('You won!')
                else:
                    await ctx.send('I won! Better luck next time!')
            elif all(self.board[0][c] != ' ' for c in range(self.columns)):
                self.game_over = True
                await ctx.send(self.print_board())
                await ctx.send('The game is a tie!')
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
        else:
            await ctx.send(f'Column {col + 1} is full!')

    #autocomplete
    async def command_autocompletion(
            interaction: discord.Interaction,
<<<<<<< HEAD
            current: str
        ) -> typing.List[app_commands.Choice[str]]:
            data = []
            for choice in ["easy", "normal", "hard"]:
=======
            current: str,
            mode: typing.Literal["easy", "normal", "hard"]
        ) -> typing.List[app_commands.Choice[str]]:
            data = []
            for choice in mode:
>>>>>>> ba2dfdb720e069a89fda978c9974818ccf16058e
                if current.lower() in choice.lower():
                    data.append(app_commands.Choice(name=choice, value=choice))
            return data
            
    @commands.hybrid_command(name="connect4", description="Play Connect 4 against MKWTASCompBot in easy, normal or hard mode!", with_app_command=True)
    @app_commands.autocomplete(mode=command_autocompletion)
<<<<<<< HEAD
    async def command(self, ctx, mode="easy"):
=======
    async def command(self, ctx, mode):
>>>>>>> ba2dfdb720e069a89fda978c9974818ccf16058e
        self.__init__(self.bot)
        self.mode = mode.lower()

        await ctx.send(f'Starting a new Connect 4 game in {mode.lower()} mode!')
        await ctx.send(self.print_board())
        await ctx.send(f'{ctx.author.mention}, it\'s your turn!')

        def check(m):
            return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= self.columns

        while not self.game_over:
            if self.current_player == 'X':
                await ctx.send(f'{ctx.author.mention}, choose a column (1-{self.columns}):')
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=60)
                    col = int(msg.content) - 1
                    await self.make_move(ctx, col, self.current_player)
                except TimeoutError:
                    await ctx.send('You took too long to respond! Game over.')
                    self.game_over = True
            else:
                if self.mode == "easy":
                    col = random.choice([c for c in range(self.columns) if self.is_valid_location(c)])
                elif self.mode == "normal":
                    col = self.minimax(4, -float('inf'), float('inf'), True)[0]
                else:
                    col = self.minimax(7, -float('inf'), float('inf'), True)[0]

                await ctx.send(f'Bot chooses column {col + 1}')
                await self.make_move(ctx, col, self.current_player)

            if not self.game_over:
                await ctx.send(self.print_board())

    def minimax(self, depth, alpha, beta, maximizing_player):
        valid_locations = [c for c in range(self.columns) if self.is_valid_location(c)]
        is_terminal = self.winning_move('X') or self.winning_move('O') or len(valid_locations) == 0
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move('O'):
                    return (None, 100000000000000)
                elif self.winning_move('X'):
                    return (None, -10000000000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position('O'))
        if maximizing_player:
            value = -float('inf')
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(col)
                b_copy = [row[:] for row in self.board]
                self.drop_piece(row, col, 'O')
                new_score = self.minimax(depth-1, alpha, beta, False)[1]
                self.board = b_copy
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:
            value = float('inf')
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(col)
                b_copy = [row[:] for row in self.board]
                self.drop_piece(row, col, 'X')
                new_score = self.minimax(depth-1, alpha, beta, True)[1]
                self.board = b_copy
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def score_position(self, piece):
        score = 0
        opponent_piece = 'X' if piece == 'O' else 'O'

        # Score center column
        center_array = [self.board[r][self.columns//2] for r in range(self.rows)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(self.rows):
            row_array = [self.board[r][c] for c in range(self.columns)]
            for c in range(self.columns-3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(self.columns):
            col_array = [self.board[r][c] for r in range(self.rows)]
            for r in range(self.rows-3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(self.rows-3):
            for c in range(self.columns-3):
                window = [self.board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Score negative sloped diagonal
        for r in range(self.rows-3):
            for c in range(self.columns-3):
                window = [self.board[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def evaluate_window(self, window, piece):
        score = 0
        opponent_piece = 'X' if piece == 'O' else 'O'
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(' ') == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(' ') == 2:
            score += 2
        if window.count(opponent_piece) == 3 and window.count(' ') == 1:
            score -= 4
        return score

async def setup(bot) -> None:
    await bot.add_cog(Connect4(bot))