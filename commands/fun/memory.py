import discord
from discord.ext import commands
import random
import asyncio

class MemoryGameView(discord.ui.View):
    def __init__(self, bot, ctx, size):
        super().__init__(timeout=60)  # The timeout for the buttons
        self.bot = bot
        self.ctx = ctx
        self.size = size
        self.game_started = False

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command initiator can start the game.", ephemeral=True)
            return

        self.game_started = True
        await interaction.response.edit_message(content="Starting the memory game!", view=None)
        self.stop()  # Ends the button interaction

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Only the command initiator can cancel the game.", ephemeral=True)
            return

        # Delete the embed message when the game is canceled
        await interaction.message.delete()
        self.stop()  # Ends the button interaction

    async def on_timeout(self):
        # This is called when the view times out (no button press in 60 seconds)
        # Delete the message when the view times out
        message = await self.ctx.fetch_message(self.ctx.message.id)
        await message.delete()

class Memory(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        # Track ongoing games at the class level
        self.ongoing_games = set()

    @commands.hybrid_command(name="memory", description="Play a memory game!", with_app_command=True)
    async def command(self, ctx, size: int = 4):
        if ctx.author.id in self.ongoing_games:
            await ctx.send("You're already playing a game!")
            return

        if size <= 0:
            return await ctx.send("Board size is too small!")

        lives = int(size - 1)

        # Create the embed for game instructions
        embed = discord.Embed(
            title="Memory Game Instructions",
            description=f"Welcome to the memory game!\n\n"
                        "In this game, a board is presented to you and you need to match all pairs of emojis to win! "
                        "To select a tile, you need to send a message in the following format: row, column\n",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Game Settings:",
            value=(f"- **Board settings**: {size}x{size}\n" f"- **Lives**: You have {lives} lives."),
            inline=False
        )

        embed.add_field(
            name="This game has a unique mechanism",
            value=(
                "\nWhen you select a tile, the surrounding tiles will briefly be revealed before becoming "
                "hidden again. Try to remember the positions of the tiles to find matching pairs!"
            ),
            inline=False
        )

        embed.set_footer(text="Click Start to begin the game, or Cancel to stop.")

        # Send embed message with interactive buttons
        view = MemoryGameView(self.bot, ctx, size)
        await ctx.send(embed=embed, view=view)

        # Wait until the user clicks "Start" or "Cancel"
        await view.wait()

        # If the game was canceled or the user didn't respond in time, exit
        if not view.game_started:
            return

        # Add the user to the ongoing games set
        self.ongoing_games.add(ctx.author.id)

        try:
            # Get list of emojis from the server
            guild_emojis = ctx.guild.emojis
            num_emojis_needed = (size * size - 1) // 2 if size % 2 != 0 else (size * size) // 2
            if len(guild_emojis) < num_emojis_needed:
                await ctx.send(f"Not enough emojis on the server for a {size}x{size} board!")
                return

            # Prepare unique pairs of emojis and shuffle the board
            unique_emojis = random.sample(guild_emojis, num_emojis_needed)
            board_emojis = unique_emojis * 2
            random.shuffle(board_emojis)

            # Create hidden board with ? placeholders
            hidden_board = [['❓' for _ in range(size)] for _ in range(size)]

            # Handle odd-sized board middle tile (❌)
            middle_pos = (size // 2, size // 2) if size % 2 != 0 else None

            # Create the display board and leave the middle tile as '❌' if board size is odd
            display_board = [
                [
                    board_emojis.pop() if middle_pos is None or (i, j) != middle_pos else '❌'
                    for j in range(size)
                ]
                for i in range(size)
            ]

            # Make sure the middle tile in hidden_board is set to '❌' if the board size is odd
            if middle_pos:
                hidden_board[middle_pos[0]][middle_pos[1]] = '❌'

            # Function to display the board in a formatted way without row numbers
            def format_board(board):
                return '\n'.join(' '.join(str(cell) for cell in row) for row in board)

            # Function to reveal a 3x3 area (Fog of War effect) around the selected tile
            def reveal_area(row, col, radius=1):
                revealed_board = [
                    ['❓' if middle_pos is None or (r, c) != middle_pos else '❌' for c in range(size)]
                    for r in range(size)
                ]
                for r in range(max(0, row - radius), min(size, row + radius + 1)):
                    for c in range(max(0, col - radius), min(size, col + radius + 1)):
                        if hidden_board[r][c] == '❓' and (r, c) != middle_pos:  # Only reveal hidden tiles, skip middle
                            revealed_board[r][c] = display_board[r][c]
                        else:
                            revealed_board[r][c] = hidden_board[r][c]  # Show already revealed/matched tiles
                return revealed_board

            # Function to update the hidden board when a match is found
            def update_hidden_board(row1, col1, row2, col2):
                hidden_board[row1][col1] = display_board[row1][col1]
                hidden_board[row2][col2] = display_board[row2][col2]

            # Function to keep only the selected tile visible, hiding the surroundings
            def keep_only_selected_visible(row, col):
                single_tile_board = [
                    ['❓' if middle_pos is None or (r, c) != middle_pos else '❌' for c in range(size)]
                    for r in range(size)
                ]
                for r in range(size):
                    for c in range(size):
                        if hidden_board[r][c] != '❓' or (r, c) == middle_pos:  # Keep matched pairs visible and middle 'X'
                            single_tile_board[r][c] = hidden_board[r][c]
                # Keep only the selected tile visible
                single_tile_board[row][col] = display_board[row][col]
                return single_tile_board

            # Send the initial hidden board
            board_message = await ctx.send(format_board(hidden_board))

            # Keep track of found pairs
            found_pairs = []

            def is_valid_choice(choice):
                # Check if the input is in the format "row,column" and within bounds (1-based)
                try:
                    row, col = map(int, choice.split(","))
                    # Ensure the player isn't selecting the middle "X" tile
                    if middle_pos and row == middle_pos[0] + 1 and col == middle_pos[1] + 1:
                        return False
                    return 1 <= row <= size and 1 <= col <= size and hidden_board[row - 1][col - 1] == '❓'
                except (ValueError, IndexError):
                    return False

            # Main game loop with timeout handling
            while lives > 0 and len(found_pairs) < size * size - (1 if middle_pos else 0):  # Adjust for missing middle tile
                try:
                    # Get first choice from the user with a 40-second timeout
                    await ctx.send(f"Select first tile! Lives remaining: {lives}")
                    msg = await self.bot.wait_for('message', timeout=40.0, check=lambda m: m.author == ctx.author and is_valid_choice(m.content))
                    row1, col1 = map(int, msg.content.split(","))
                    row1 -= 1  # Adjust for 0-based indexing
                    col1 -= 1

                    # Reveal the 3x3 area around the first choice
                    fogged_board = reveal_area(row1, col1)
                    await board_message.edit(content=format_board(fogged_board))  # Edit instead of delete

                    # Wait a short moment, then show only the selected tile
                    await asyncio.sleep(0.3)
                    visible_only_selected = keep_only_selected_visible(row1, col1)
                    await board_message.edit(content=format_board(visible_only_selected))  # Edit instead of delete

                    # Get second choice from the user with a 40-second timeout
                    await ctx.send(f"Select second tile! Lives remaining: {lives}")
                    msg = await self.bot.wait_for('message', timeout=40.0, check=lambda m: m.author == ctx.author and is_valid_choice(m.content))
                    row2, col2 = map(int, msg.content.split(","))
                    row2 -= 1  # Adjust for 0-based indexing
                    col2 -= 1

                    # Reveal the 3x3 area around the second choice
                    fogged_board = reveal_area(row2, col2)
                    await board_message.edit(content=format_board(fogged_board))  # Edit instead of delete

                    # Wait a short moment, then show only the selected tile
                    await asyncio.sleep(0.3)
                    visible_only_selected = keep_only_selected_visible(row2, col2)
                    await board_message.edit(content=format_board(visible_only_selected))  # Edit instead of delete

                    # Check if the two selected tiles match
                    if display_board[row1][col1] == display_board[row2][col2]:
                        await ctx.send("It's a match!")
                        update_hidden_board(row1, col1, row2, col2)
                        found_pairs.append((row1, col1))
                        found_pairs.append((row2, col2))
                    else:
                        await ctx.send("Not a match. The tiles will be hidden again.")
                        lives -= 1  # Decrease lives if no match
                        await asyncio.sleep(1)  # Pause briefly before hiding again

                    # Delete the old board message
                    await board_message.delete()

                    # Redisplay the full board with updated hidden/matched pairs after the full round
                    board_message = await ctx.send(format_board(hidden_board))

                except asyncio.TimeoutError:
                    await ctx.send("Game expired due to inactivity. You took too long to respond.")
                    break

            # End game messages
            if lives == 0:
                await ctx.send("Game over! You're out of lives.")
            elif len(found_pairs) == size * size - (1 if middle_pos else 0):  # Adjust for missing middle tile
                await ctx.send("Congratulations! You found all pairs!")
            else:
                await ctx.send("The game has ended due to inactivity.")

        finally:
            # Remove the user from the ongoing games set after the game finishes or expires
            self.ongoing_games.remove(ctx.author.id)


# Setup the cog
async def setup(bot) -> None:
    await bot.add_cog(Memory(bot))
