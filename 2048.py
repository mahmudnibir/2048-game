import pygame
import random

# Initialize Pygame
pygame.init()

# Set up constants
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (187, 173, 160)
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
FONT = pygame.font.SysFont('arial', 32)

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

# Sound effects (You can replace these with actual sound files)
# MOVE_SOUND = pygame.mixer.Sound("move.wav")
# MERGE_SOUND = pygame.mixer.Sound("merge.wav")

# Game grid
def create_grid():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

def add_random_tile(grid):
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        grid[r][c] = random.choice([2, 4])

def draw_grid(grid):
    screen.fill(BACKGROUND_COLOR)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = grid[r][c]
            pygame.draw.rect(screen, TILE_COLORS.get(value, (205, 193, 180)), pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if value:
                text = FONT.render(str(value), True, (119, 110, 101) if value <= 4 else (255, 255, 255))
                text_rect = text.get_rect(center=(c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

    pygame.display.flip()

def move_left(grid):
    moved = False
    for r in range(GRID_SIZE):
        non_zero = [x for x in grid[r] if x != 0]
        new_row = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                new_row.append(non_zero[i] * 2)
                i += 2
               #  MERGE_SOUND.play()
            else:
                new_row.append(non_zero[i])
                i += 1
        new_row += [0] * (GRID_SIZE - len(new_row))
        if grid[r] != new_row:
            moved = True
        grid[r] = new_row
    return moved

def rotate_grid(grid):
    return [list(row) for row in zip(*grid)]

def move(grid, direction):
    moved = False
    if direction == "left":
        moved = move_left(grid)
    elif direction == "right":
        grid = [row[::-1] for row in grid]
        moved = move_left(grid)
        grid = [row[::-1] for row in grid]
    elif direction == "up":
        grid = rotate_grid(grid)
        moved = move_left(grid)
        grid = rotate_grid(grid)
    elif direction == "down":
        grid = rotate_grid(grid)
        grid = [row[::-1] for row in grid]
        moved = move_left(grid)
        grid = [row[::-1] for row in grid]
        grid = rotate_grid(grid)
    return moved, grid

# Main game loop
def main():
    grid = create_grid()
    add_random_tile(grid)
    add_random_tile(grid)

    clock = pygame.time.Clock()
    game_over = False
    while not game_over:
        draw_grid(grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    moved, grid = move(grid, "left")
                elif event.key == pygame.K_RIGHT:
                    moved, grid = move(grid, "right")
                elif event.key == pygame.K_UP:
                    moved, grid = move(grid, "up")
                elif event.key == pygame.K_DOWN:
                    moved, grid = move(grid, "down")

                if moved:
                    add_random_tile(grid)
                    # MOVE_SOUND.play()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
