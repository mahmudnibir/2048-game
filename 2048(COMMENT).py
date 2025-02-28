import pygame
import random
import copy
import json
import os

# Initialize Pygame library and set up configurations
pygame.init()

# Constants to define screen size, grid dimensions, tile colors, etc.
WIDTH, HEIGHT = 400, 500  # Screen width and height
GRID_SIZE = 4  # Grid size (4x4 for standard 2048 game)
CELL_SIZE = WIDTH // GRID_SIZE  # Size of each cell in the grid
WHITE = (255, 255, 255)  # White color for text and tiles
BACKGROUND_COLOR = (187, 173, 160)  # Background color of the game
SCORE_PANEL_COLOR = (119, 110, 101)  # Color of the score panel
# Tile colors corresponding to various tile values
TILE_COLORS = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
    16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97), 512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46)
}
FONT = pygame.font.SysFont('arial', 32)  # Font for tile values
SCORE_FONT = pygame.font.SysFont('arial', 24)  # Font for displaying score and high score
HIGH_SCORE_FILE = "highscore.json"  # File to save high score

# Set up the display screen with defined width and height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")  # Window title

def create_grid():
    """Initializes the grid to be a 4x4 matrix with all zeros (empty spaces)."""
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

def add_random_tile(grid):
    """
    Adds a random tile (2 or 4) at an empty position in the grid.
    It picks a random empty cell and assigns it a value of 2 or 4.
    """
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        grid[r][c] = random.choice([2, 4])

def draw_grid(grid, score, highscore, game_over=False):
    """
    Renders the entire game grid on the screen.
    Displays the grid, score panel, and game over message if applicable.
    """
    screen.fill(BACKGROUND_COLOR)  # Fill background with the specified color
    pygame.draw.rect(screen, SCORE_PANEL_COLOR, pygame.Rect(0, 0, WIDTH, 100))  # Score panel background
    score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)  # Score text
    highscore_text = SCORE_FONT.render(f"High Score: {highscore}", True, WHITE)  # High score text
    screen.blit(score_text, (20, 30))  # Position and draw score text
    screen.blit(highscore_text, (220, 30))  # Position and draw high score text
    
    # Render each grid cell (tile) on the screen
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            pygame.draw.rect(screen, TILE_COLORS.get(value, (205, 193, 180)), pygame.Rect(c * CELL_SIZE, r * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE))  # Draw the cell with appropriate color
            if value:
                # Render the value inside the tile (number)
                text = FONT.render(str(value), True, (119, 110, 101) if value <= 4 else (255, 255, 255))
                text_rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + 100 + CELL_SIZE // 2))  # Position the text in the center of the cell
                screen.blit(text, text_rect)  # Draw the value text on the tile
    
    # If the game is over, display a "Game Over" message
    if game_over:
        game_over_text = FONT.render("Game Over!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
    
    pygame.display.flip()  # Update the screen with the drawn elements

def move_left(grid, score):
    """
    Handles the tile movement and merging logic when moving the tiles to the left.
    This function combines adjacent tiles with the same value and updates the score accordingly.
    Returns a boolean indicating if a move was made, and the updated score.
    """
    moved = False
    for r in range(GRID_SIZE):
        non_zero = [x for x in grid[r] if x != 0]  # List of non-zero values in the row
        new_row = []
        i = 0
        while i < len(non_zero):
            # Merge tiles with the same value
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                new_row.append(merged_value)
                score += merged_value  # Add the merged value to the score
                i += 2  # Skip the next tile as it has been merged
            else:
                new_row.append(non_zero[i])
                i += 1
        new_row += [0] * (GRID_SIZE - len(new_row))  # Add zeros at the end to maintain row size
        if grid[r] != new_row:
            moved = True  # The row has been modified, indicating a move was made
        grid[r] = new_row  # Update the row in the grid
    return moved, score

def rotate_grid(grid):
    """Rotates the grid 90 degrees clockwise."""
    return [list(row) for row in zip(*grid)]  # Rotate by transposing and reversing rows

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
        grid = [row[::-1] for row in grid]  # Reverse rows to simulate a left move
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]  # Reverse back to original direction
    elif direction == "up":
        grid = rotate_grid(grid)  # Rotate grid to handle up movement as left
        moved, score = move_left(grid, score)
        grid = rotate_grid(grid)  # Rotate back to original direction
    elif direction == "down":
        grid = rotate_grid(grid)  # Rotate grid to handle down movement as left
        grid = [row[::-1] for row in grid]  # Reverse rows
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]  # Reverse back to original direction
        grid = rotate_grid(grid)  # Rotate back to original direction
    return moved, grid, score

def is_game_over(grid):
    """
    Checks if the game is over.
    The game is over if there are no empty cells and no adjacent tiles with the same value.
    """
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:  # If there's any empty cell, the game is not over
                return False
            if c < GRID_SIZE - 1 and grid[r][c] == grid[r][c + 1]:  # Check horizontal adjacency
                return False
            if r < GRID_SIZE - 1 and grid[r][c] == grid[r + 1][c]:  # Check vertical adjacency
                return False
    return True  # If no empty cells and no adjacent matching tiles, the game is over

def save_highscore(score):
    """
    Saves the new high score to a file if the current score is higher than the previous high score.
    """
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            highscore = json.load(file)
    else:
        highscore = 0  # Default highscore if file doesn't exist
    if score > highscore:
        with open(HIGH_SCORE_FILE, 'w') as file:
            json.dump(score, file)  # Save new high score to the file

def load_highscore():
    """
    Loads the high score from a file.
    Returns 0 if the file doesn't exist.
    """
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return json.load(file)
    return 0  # Return 0 if no high score is stored

def main():
    """
    Main game loop that runs the game.
    It initializes the grid, handles user input, and updates the game state accordingly.
    """
    grid = create_grid()  # Initialize an empty grid
    add_random_tile(grid)  # Add two random tiles to start the game
    add_random_tile(grid)
    score = 0  # Initial score
    highscore = load_highscore()  # Load high score from file
    game_over = False  # Flag to indicate if the game is over
    clock = pygame.time.Clock()  # Clock object to manage frame rate
    
    while True:
        draw_grid(grid, score, highscore, game_over)  # Draw the grid and UI elements
        if game_over:
            pygame.time.wait(2000)  # Wait for 2 seconds before quitting the game
            break
        
        for event in pygame.event.get():  # Handle user input events
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                moved = False
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    direction = {pygame.K_LEFT: "left", pygame.K_RIGHT: "right", pygame.K_UP: "up", pygame.K_DOWN: "down"}[event.key]
                    moved, grid, score = move(grid, direction, score)  # Move tiles based on user input
                    if moved:
                        add_random_tile(grid)  # Add a new tile after a valid move
                        if is_game_over(grid):  # Check if the game is over after the move
                            save_highscore(score)  # Save high score if game is over
                            game_over = True
        
        clock.tick(10)  # Set frame rate to 10 frames per second
    pygame.quit()  # Quit Pygame when the game is over

if __name__ == "__main__":
    main()  # Start the game when the script is executed    
