import pygame
import random
import copy

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

# Sounds (replace paths with actual files if needed)
# pygame.mixer.init()
# MOVE_SOUND = pygame.mixer.Sound("move.wav")
# MERGE_SOUND = pygame.mixer.Sound("merge.wav")

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

def draw_grid(grid, score):
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, SCORE_PANEL_COLOR, pygame.Rect(0, 0, WIDTH, 100))
    score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 30))
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            pygame.draw.rect(screen, TILE_COLORS.get(value, (205, 193, 180)), pygame.Rect(c * CELL_SIZE, r * CELL_SIZE + 100, CELL_SIZE, CELL_SIZE))
            if value:
                text = FONT.render(str(value), True, (119, 110, 101) if value <= 4 else (255, 255, 255))
                text_rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + 100 + CELL_SIZE // 2))
                screen.blit(text, text_rect)
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
                # MERGE_SOUND.play()
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

def main():
    grid = create_grid()
    add_random_tile(grid)
    add_random_tile(grid)
    score = 0
    history = []
    
    clock = pygame.time.Clock()
    game_over = False
    while not game_over:
        history.append(copy.deepcopy(grid))
        draw_grid(grid, score)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                moved = False
                if event.key == pygame.K_LEFT:
                    moved, grid, score = move(grid, "left", score)
                elif event.key == pygame.K_RIGHT:
                    moved, grid, score = move(grid, "right", score)
                elif event.key == pygame.K_UP:
                    moved, grid, score = move(grid, "up", score)
                elif event.key == pygame.K_DOWN:
                    moved, grid, score = move(grid, "down", score)
                elif event.key == pygame.K_r:
                    grid = create_grid()
                    add_random_tile(grid)
                    add_random_tile(grid)
                    score = 0
                elif event.key == pygame.K_u and len(history) > 1:
                    grid = history.pop(-2)
                
                if moved:
                    add_random_tile(grid)
                    # MOVE_SOUND.play()
                if is_game_over(grid):
                    print("Game Over! Final Score:", score)
                    game_over = True
        
        clock.tick(10)
    pygame.quit()

if __name__ == "__main__":
    main()
