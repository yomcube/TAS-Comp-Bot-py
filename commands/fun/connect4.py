import discord
from discord.ext import commands
from discord import app_commands
import typing
import random
import asyncio


class Connect4(commands.Cog):
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
        self.last_board_message = None
        self.is_bot_game = False

    def reset_game(self):
        self.board = [[' ' for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_player = 'X'
        self.game_over = False
        self.players = {}
        self.game_channel = None
        self.last_board_message = None
        self.is_bot_game = False

    def print_board(self):
        #board_string = '```\n'
        board_string = ''
        emoji_map = {'X': ':red_circle:\u200a', 'O': ':yellow_circle:\u200a', ' ': ':white_circle:\u200a'}
        for row in self.board:
            board_string += ''.join(emoji_map[cell] for cell in row) + '\n'
        #board_string += '```'
        return board_string

    def is_valid_location(self, col):
        return self.board[0][col] == ' '

    def get_next_open_row(self, col):
        for r in range(self.rows - 1, -1, -1):
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

    async def make_move(self, col, piece):
        if col < 0 or col >= self.columns:
            await self.game_channel.send("Invalid column! Please select a column between 1 and 7.")
            return

        if self.is_valid_location(col):
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, piece)
            await self.update_board_message()
            if self.winning_move(piece):
                self.game_over = True
                winner = self.players[piece]
                await self.game_channel.send(f'Congratulations {winner.mention}, you won!')
            elif all(self.board[0][c] != ' ' for c in range(self.columns)):
                self.game_over = True
                await self.game_channel.send('The game is a tie!')
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                if not self.is_bot_game or self.current_player == 'X':
                    await self.game_channel.send(f'It\'s {self.players[self.current_player].mention}\'s turn!')

                # handle inactivity
                if self.timeout_task:
                    self.timeout_task.cancel()  # Cancel the existing timer task
                self.timeout_task = self.bot.loop.create_task(self.start_timer())  # Start a new timer task
        else:
            await self.game_channel.send(f'Column {col + 1} is full!')

    async def update_board_message(self):
        if self.last_board_message:
            await self.last_board_message.delete()
        embed = discord.Embed(description = self.print_board())
        self.last_board_message = await self.game_channel.send(embed = embed)

    async def send_challenge(self, ctx, opponent):
        view = ChallengeView(self, ctx, opponent)
        challenge_message = await ctx.send(
            f'{opponent.mention}, you have been challenged to a Connect 4 duel by {ctx.author.mention}!',
            view=view
        )
        self.pending_challenges[opponent.id] = challenge_message

    async def handle_button_click(self, interaction, ctx, opponent):
        if interaction.data['custom_id'] == "accept":
            opponent_id = interaction.user.id
            if opponent_id in self.pending_challenges:
                challenge_message = self.pending_challenges[opponent_id]
                await challenge_message.delete()
                del self.pending_challenges[opponent_id]
                await self.start_game(ctx, opponent)
        elif interaction.data['custom_id'] == "decline":
            opponent_id = interaction.user.id
            if opponent_id in self.pending_challenges:
                challenge_message = self.pending_challenges[opponent_id]
                await challenge_message.delete()
                del self.pending_challenges[opponent_id]

    async def start_game(self, ctx, opponent):
        self.reset_game()
        self.players = {'X': ctx.author, 'O': opponent}
        self.game_channel = ctx.channel
        self.is_bot_game = opponent == self.bot.user

        await self.game_channel.send(f'Starting a new Connect 4 game! {ctx.author.mention} vs {opponent.mention}')
        await self.update_board_message()
        await self.game_channel.send(f'{ctx.author.mention}, it\'s your turn!')

        def check(m):
            return m.author == self.players[self.current_player] and m.content.isdigit() and 1 <= int(
                m.content) <= self.columns

        while not self.game_over:
            if not self.is_bot_game or self.current_player == 'X':
                await self.game_channel.send(
                    f'{self.players[self.current_player].mention}, choose a column (1-{self.columns}):')
                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=60)
                    col = int(msg.content) - 1
                    await self.make_move(col, self.current_player)
                except asyncio.TimeoutError:
                    await self.game_channel.send('You took too long to respond! Game over.')
                    self.game_over = True
            else:
                await self.game_channel.send('Bot is thinking...')
                col = await self.bot_move()
                await self.game_channel.send(f'Bot chooses column {col + 1}')
                await self.make_move(col, self.current_player)

            if not self.game_over:
                await self.update_board_message()

    async def bot_move(self):
        await asyncio.sleep(1)  # Simulate thinking time
        if self.mode == "easy":
            col = random.choice([c for c in range(self.columns) if self.is_valid_location(c)])
        elif self.mode == "normal":
            col = self.minimax(3, -float('inf'), float('inf'), True)[0]
        else:
            col = self.minimax(6, -float('inf'), float('inf'), True)[0]  # Reduce depth for faster moves
        return col

    async def command_autocompletion(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> typing.List[app_commands.Choice[str]]:
        modes = ["easy", "normal", "hard"]
        return [
            app_commands.Choice(name=mode, value=mode)
            for mode in modes if current.lower() in mode.lower()
        ]

    @commands.hybrid_command(
        name="connect4",
        description="Play Connect 4 against MKWTASCompBot in easy, normal or hard mode!",
        with_app_command=True
    )
    @app_commands.autocomplete(mode=command_autocompletion)
    async def command(self, ctx: commands.Context, opponent: discord.Member = None, mode: str = "easy"):
        self.reset_game()
        self.mode = mode.lower()

        if self.game_over or len(self.players) == 0:
            if opponent == self.bot.user:
                # Start the game directly with the bot
                await self.start_game(ctx, self.bot.user)
            else:
                self.reset_game()
                self.players['X'] = ctx.author
                self.players['O'] = opponent
                self.game_channel = ctx.channel

                await self.send_challenge(ctx, opponent)
        else:
            await ctx.send('A game is already in progress. Please wait for it to finish before starting a new one.')

    async def send_message(self, ctx, message):
        if isinstance(ctx, commands.Context):
            await ctx.send(message)
        else:
            if ctx.response.is_done():
                await ctx.followup.send(message)
            else:
                await ctx.response.send_message(message)

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
                self.drop_piece(row, col, 'O')
                new_score = self.minimax(depth - 1, alpha, beta, False)[1]
                self.board[row][col] = ' '  # Undo move
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
                self.drop_piece(row, col, 'X')
                new_score = self.minimax(depth - 1, alpha, beta, True)[1]
                self.board[row][col] = ' '  # Undo move
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
        center_array = [self.board[r][self.columns // 2] for r in range(self.rows)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Score Horizontal
        for r in range(self.rows):
            row_array = [self.board[r][c] for c in range(self.columns)]
            for c in range(self.columns - 3):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, piece)

        # Score Vertical
        for c in range(self.columns):
            col_array = [self.board[r][c] for r in range(self.rows)]
            for r in range(self.rows - 3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, piece)

        # Score positive sloped diagonal
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                window = [self.board[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        # Score negative sloped diagonal
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                window = [self.board[r + 3 - i][c + i] for i in range(4)]
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


class ChallengeView(discord.ui.View):
    def __init__(self, cog, ctx, opponent):
        super().__init__(timeout=60)
        self.cog = cog
        self.ctx = ctx
        self.opponent = opponent

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged player!", ephemeral=True)
            return

        await interaction.response.send_message(f"{interaction.user.mention} accepted the challenge!")
        await self.cog.handle_button_click(interaction, self.ctx, self.opponent)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, custom_id="decline")
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.opponent:
            await interaction.response.send_message("You are not the challenged player!", ephemeral=True)
            return

        await interaction.response.send_message(f"{interaction.user.mention} declined the challenge.")
        await self.cog.handle_button_click(interaction, self.ctx, self.opponent)
        self.stop()


async def setup(bot) -> None:
    await bot.add_cog(Connect4(bot))

