import pygame
import random
import copy
import json
import os

# Initialize Pygame library and set up configurations
pygame.init()


console.log("This is not a mobile responsive")
# Constants to define screen size, grid dimensions, tile colors, etc.

WIDTH, HEIGHT = 400, 500                 # Screen width and height in pixels
GRID_SIZE = 4                            # Grid size (4x4 grid for standard 2048 game)
CELL_SIZE = WIDTH // GRID_SIZE           # Size of each cell in the grid, based on screen width
WHITE = (255, 255, 255)                  # White color for text and tile values
BACKGROUND_COLOR = (187, 173, 160)       # Background color of the game
SCORE_PANEL_COLOR = (119, 110, 101)      # Color of the score panel at the top



# ==============================================
#           Tile Colors Corresponding          =
#             To Various Tile Values           =
# ==============================================

TILE_COLORS = {
    2: (238, 228, 218), 
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),        
    32: (246, 124, 95),        
    64: (246, 94, 59), 
    128: (237, 207, 114), 
    256: (237, 204, 97), 
    512: (237, 200, 80), 
    1024: (237, 197, 63), 
    2048: (237, 194, 46)
}

FONT = pygame.font.SysFont('arial', 32)            # Font for tile values
SCORE_FONT = pygame.font.SysFont('arial', 24)      # Font for displaying score and high score


HIGH_SCORE_FILE = "highscore.json"                 # Path for the high score file

screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Create a window with the specified dimensions
pygame.display.set_caption("2048")                 # Set the window title


MELD_SOUND = pygame.mixer.Sound('sound.mp3')       # Sound effect for merging tiles


clock = pygame.time.Clock()                        # Game clock for controlling the game's frame rate
SPEED_MULTIPLIER = 1                               # Initial speed multiplier for the game


def create_grid():
    """Initializes the grid to be a 4x4 matrix with all zeros (empty spaces)."""
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]  # Return a grid filled with zeros


def add_random_tile(grid):
    """
    Adds a random tile (2 or 4) at an empty position in the grid.
    It picks a random empty cell and assigns it a value of 2 or 4.
    """
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]  # List of empty cells
    if empty_cells:                                 # If there are any empty cells
        r, c = random.choice(empty_cells)           # Choose a random empty cell
        grid[r][c] = random.choice([2, 4])          # Assign a random value (2 or 4) to the chosen cell


def draw_grid(grid, score, highscore, game_over=False):
    """
    Renders the entire game grid on the screen.
    Displays the grid, score panel, and game over message if applicable.
    """
    screen.fill(BACKGROUND_COLOR)                                                    # Fill the background with the defined color
    pygame.draw.rect(screen, SCORE_PANEL_COLOR, pygame.Rect(0, 0, WIDTH, 100))       # Draw score panel at the top
    score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)                   # Render the current score text
    highscore_text = SCORE_FONT.render(f"High Score: {highscore}", True, WHITE)      # Render high score text
    screen.blit(score_text, (20, 30))                                                # Draw the current score text at the specified position
    screen.blit(highscore_text, (220, 30))                                           # Draw the high score text at the specified position
    
    
    for r in range(GRID_SIZE):                                                       # Render each grid cell (tile) on the screen
        for c in range(GRID_SIZE):
            value = grid[r][c]                                                       # Value of the current tile
            pygame.draw.rect(screen, TILE_COLORS.get(value, (205, 193, 180)), pygame.Rect(c * CELL_SIZE, r * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE))  # Draw the cell with appropriate color
            if value:                                                                # If the tile has a value (non-zero)
                 # Render the value inside the tile (number)
                text = FONT.render(str(value), True, (119, 110, 101) if value <= 4 else (255, 255, 255))  # Choose text color based on tile value
                text_rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + 100 + CELL_SIZE // 2))  # Position the text in the center of the cell
                screen.blit(text, text_rect)                  # Draw the value text on the tile
    

    if game_over:
        game_over_text = FONT.render("Game Over!", True, WHITE)                # Render "Game Over" text
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Position the text in the center of the screen
        screen.blit(game_over_text, text_rect)                                 # Draw the "Game Over" message
    
    pygame.display.flip()                                                      # Update the screen with the drawn elements


def move_left(grid, score):
    """
    Handles the tile movement and merging logic when moving the tiles to the left.
    This function combines adjacent tiles with the same value and updates the score accordingly.
    Returns a boolean indicating if a move was made, and the updated score.
    """
    moved = False                                                              # Flag to indicate if the grid was moved
    for r in range(GRID_SIZE):
        non_zero = [x for x in grid[r] if x != 0]                              # List of non-zero values in the row
        new_row = []                                                           # New row after merging and shifting tiles
        i = 0
        while i < len(non_zero):
            # Merge tiles with the same value
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2                                 # Double the tile value after merging
                new_row.append(merged_value)                                   # Append the merged value to the new row
                score += merged_value                                          # Add the merged value to the score
                MELD_SOUND.play(maxtime=200)                                   # Play sound when tiles merge
                global SPEED_MULTIPLIER
                SPEED_MULTIPLIER *= 2                                          # Double the speed after a merge
                i += 2                                                         # Skip the next tile as it has been merged
            else:
                new_row.append(non_zero[i])                                    # Keep the current tile in the new row
                i += 1
        new_row += [0] * (GRID_SIZE - len(new_row))       # Add zeros at the end to maintain row size
        if grid[r] != new_row:
            moved = True                                  # The row has been modified, indicating a move was made
        grid[r] = new_row                                 # Update the row in the grid
    return moved, score                                   # Return if the move was successful and the updated score


def rotate_grid(grid):
    """Rotates the grid 90 degrees clockwise."""
    return [list(row) for row in zip(*grid)]              # Rotate by transposing and reversing rows


def move(grid, direction, score):
    """
    Handles movement in all four possible directions (left, right, up, down).
    This calls the respective move function and rotates the grid as necessary.
    Returns a tuple: moved status, updated grid, and score.
    """
    moved = False
    if direction == "left":
        moved, score = move_left(grid, score)
    elif direction == "right":
        grid = [row[::-1] for row in grid]          # Reverse rows to simulate a left move
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]          # Reverse back to original direction
    elif direction == "up":
        grid = rotate_grid(grid)                    # Rotate grid to handle up movement as left
        moved, score = move_left(grid, score)
        grid = rotate_grid(grid)                    # Rotate back to original direction
    elif direction == "down":
        grid = rotate_grid(grid)                    # Rotate grid to handle down movement as left
        grid = [row[::-1] for row in grid]          # Reverse rows
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]          # Reverse back to original direction
        grid = rotate_grid(grid)                    # Rotate back to original direction
    return moved, grid, score                       # Return if a move was made, the updated grid, and the score


def is_game_over(grid):
    """
    Checks if the game is over.
    The game is over if there are no empty cells and no adjacent tiles with the same value.
    """
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:                                     # If there's any empty cell, the game is not over
                return False
            if c < GRID_SIZE - 1 and grid[r][c] == grid[r][c + 1]:  # Check horizontal adjacency
                return False
            if r < GRID_SIZE - 1 and grid[r][c] == grid[r + 1][c]:  # Check vertical adjacency
                return False
    return True                                                     # If no empty cells and no adjacent matching tiles, the game is over


def save_highscore(score):
    """
    Saves the new high score to a file if the current score is higher than the previous high score.
    """
    if os.path.exists(HIGH_SCORE_FILE):              # If the high score file exists
        with open(HIGH_SCORE_FILE, 'r') as file:
            highscore = json.load(file)              # Read the current high score
    else:
        highscore = 0                                # If no high score file exists, initialize high score to 0
    if score > highscore:                            # If the current score is higher than the stored high score
        with open(HIGH_SCORE_FILE, 'w') as file:
            json.dump(score, file)                   # Save the new high score


def load_highscore():
    """Loads the high score from the file."""
    if os.path.exists(HIGH_SCORE_FILE):              # If the high score file exists
        with open(HIGH_SCORE_FILE, 'r') as file:
            return json.load(file)                   # Read and return the high score
    return 0                                         # If no file exists, return a default high score of 0


def main():
    """
    Main game loop. Handles events (key presses), updates the game state (grid, score),
    and draws the game on the screen.
    """
    grid = create_grid()             # Initialize an empty grid
    add_random_tile(grid)            # Add the first random tile
    score = 0                        # Initialize the score
    highscore = load_highscore()     # Load the high score
    game_over = False                # Flag to indicate if the game is over

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Handle arrow key inputs to move the tiles
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_LEFT:
                    moved, grid, score = move(grid, "left", score)
                elif event.key == pygame.K_RIGHT:
                    moved, grid, score = move(grid, "right", score)
                elif event.key == pygame.K_UP:
                    moved, grid, score = move(grid, "up", score)
                elif event.key == pygame.K_DOWN:
                    moved, grid, score = move(grid, "down", score)

                # If the grid was moved, add a new random tile
                if moved:
                    add_random_tile(grid)

                # Check if the game is over
                game_over = is_game_over(grid)

        # Render the game grid and score
        draw_grid(grid, score, highscore, game_over)

    # Save high score if needed
    save_highscore(score)

# Run the game
if __name__ == "__main__":
    main()  # Start the main game loop
