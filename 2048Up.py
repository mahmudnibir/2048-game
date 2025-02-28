import pygame
import random
import json
import numpy as np

# Constants
GRID_SIZE = 4
TILE_SIZE = 100
GAP = 10
WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GAP, GRID_SIZE * TILE_SIZE + (GRID_SIZE + 1) * GAP + 80
FPS = 60

# Colors
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLORS = {
    0: (205, 193, 180),
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

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048 Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

# Load high score
try:
    with open("highscore.json", "r") as f:
        high_score = json.load(f)["highscore"]
except:
    high_score = 0

def save_high_score():
    with open("highscore.json", "w") as f:
        json.dump({"highscore": high_score}, f)

def add_new_tile(board):
    empty_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 2 if random.random() < 0.9 else 4

def draw_board(board, score):
    screen.fill(BACKGROUND_COLOR)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            value = board[r][c]
            color = TILE_COLORS.get(value, (60, 58, 50))
            pygame.draw.rect(screen, color, (c * (TILE_SIZE + GAP) + GAP, r * (TILE_SIZE + GAP) + GAP, TILE_SIZE, TILE_SIZE))
            if value:
                text = font.render(str(value), True, (0, 0, 0) if value < 8 else (255, 255, 255))
                screen.blit(text, (c * (TILE_SIZE + GAP) + GAP + TILE_SIZE // 2 - text.get_width() // 2, 
                                   r * (TILE_SIZE + GAP) + GAP + TILE_SIZE // 2 - text.get_height() // 2))
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, HEIGHT - 60))
    high_score_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    screen.blit(high_score_text, (WIDTH - 180, HEIGHT - 60))

def can_move(board):
    temp = board.copy()
    for _ in range(4):
        temp = np.rot90(temp)
        if any(merge(row) != row for row in temp):
            return True
    return False

def merge(row):
    new_row = [num for num in row if num != 0]
    for i in range(len(new_row) - 1):
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            new_row[i + 1] = 0
    return [num for num in new_row if num != 0] + [0] * (GRID_SIZE - len(new_row))

def move(board, direction):
    global high_score
    prev_board = board.copy()
    board = np.rot90(board, direction)
    board = np.array([merge(row) for row in board])
    board = np.rot90(board, -direction)
    if not np.array_equal(board, prev_board):
        add_new_tile(board)
    return board

def main():
    global high_score
    board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    add_new_tile(board)
    add_new_tile(board)
    score = 0
    running = True
    history = []

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    history.append(board.copy())
                    direction = {pygame.K_LEFT: 0, pygame.K_UP: 1, pygame.K_RIGHT: 2, pygame.K_DOWN: 3}[event.key]
                    new_board = move(board, direction)
                    if not np.array_equal(board, new_board):
                        board = new_board
                        score = board.sum()
                        if score > high_score:
                            high_score = score
                            save_high_score()
                elif event.key == pygame.K_r:  # Restart game
                    board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
                    add_new_tile(board)
                    add_new_tile(board)
                    score = 0
                    history.clear()
                elif event.key == pygame.K_u and history:  # Undo move
                    board = history.pop()
        
        draw_board(board, score)
        pygame.display.flip()
        
        if not can_move(board):
            screen.fill(BACKGROUND_COLOR)
            game_over_text = font.render("Game Over! Press R to Restart", True, (0, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
            add_new_tile(board)
            add_new_tile(board)
            score = 0
            history.clear()
    pygame.quit()

if __name__ == "__main__":
    main()
