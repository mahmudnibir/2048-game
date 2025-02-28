import pygame
import random
import copy
import json
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 500
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (187, 173, 160)
SCORE_PANEL_COLOR = (119, 110, 101)
TILE_COLORS = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
    16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97), 512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46)
}
FONT = pygame.font.SysFont('arial', 32)
SCORE_FONT = pygame.font.SysFont('arial', 24)
HIGH_SCORE_FILE = "highscore.json"

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

def create_grid():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

def add_random_tile(grid):
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        grid[r][c] = random.choice([2, 4])

def draw_grid(grid, score, highscore, game_over=False):
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, SCORE_PANEL_COLOR, pygame.Rect(0, 0, WIDTH, 100))
    score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
    highscore_text = SCORE_FONT.render(f"High Score: {highscore}", True, WHITE)
    screen.blit(score_text, (20, 30))
    screen.blit(highscore_text, (220, 30))
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            pygame.draw.rect(screen, TILE_COLORS.get(value, (205, 193, 180)), pygame.Rect(c * CELL_SIZE, r * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE))
            if value:
                text = FONT.render(str(value), True, (119, 110, 101) if value <= 4 else (255, 255, 255))
                text_rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + 100 + CELL_SIZE // 2))
                screen.blit(text, text_rect)
    
    if game_over:
        game_over_text = FONT.render("Game Over!", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
    
    pygame.display.flip()

def move_left(grid, score):
    moved = False
    for r in range(GRID_SIZE):
        non_zero = [x for x in grid[r] if x != 0]
        new_row = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                new_row.append(merged_value)
                score += merged_value
                i += 2
            else:
                new_row.append(non_zero[i])
                i += 1
        new_row += [0] * (GRID_SIZE - len(new_row))
        if grid[r] != new_row:
            moved = True
        grid[r] = new_row
    return moved, score

def rotate_grid(grid):
    return [list(row) for row in zip(*grid)]

def move(grid, direction, score):
    moved = False
    if direction == "left":
        moved, score = move_left(grid, score)
    elif direction == "right":
        grid = [row[::-1] for row in grid]
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]
    elif direction == "up":
        grid = rotate_grid(grid)
        moved, score = move_left(grid, score)
        grid = rotate_grid(grid)
    elif direction == "down":
        grid = rotate_grid(grid)
        grid = [row[::-1] for row in grid]
        moved, score = move_left(grid, score)
        grid = [row[::-1] for row in grid]
        grid = rotate_grid(grid)
    return moved, grid, score

def is_game_over(grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                return False
            if c < GRID_SIZE - 1 and grid[r][c] == grid[r][c + 1]:
                return False
            if r < GRID_SIZE - 1 and grid[r][c] == grid[r + 1][c]:
                return False
    return True

def save_highscore(score):
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            highscore = json.load(file)
    else:
        highscore = 0
    if score > highscore:
        with open(HIGH_SCORE_FILE, 'w') as file:
            json.dump(score, file)

def load_highscore():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'r') as file:
            return json.load(file)
    return 0

def main():
    grid = create_grid()
    add_random_tile(grid)
    add_random_tile(grid)
    score = 0
    highscore = load_highscore()
    game_over = False
    clock = pygame.time.Clock()
    
    while True:
        draw_grid(grid, score, highscore, game_over)
        if game_over:
            pygame.time.wait(2000)
            break
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                moved = False
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    direction = {pygame.K_LEFT: "left", pygame.K_RIGHT: "right", pygame.K_UP: "up", pygame.K_DOWN: "down"}[event.key]
                    moved, grid, score = move(grid, direction, score)
                    if moved:
                        add_random_tile(grid)
                        if is_game_over(grid):
                            save_highscore(score)
                            game_over = True
        
        clock.tick(10)
    pygame.quit()

if __name__ == "__main__":
    main()
