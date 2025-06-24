import pygame

pygame.init()

# Screen setup
screen = pygame.display.set_mode((640, 720))
pygame.display.set_caption("minos")

clock = pygame.time.Clock()

# Grid configuration
CELL_SIZE = 32
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = 100
GRID_OFFSET_Y = 40

# Timing
fall_interval = 0.5  # normal gravity
fall_timer = 0

# DAS/ARR
DAS = 0.15
ARR = 0.05
key_hold = {"left": 0, "right": 0}
move_dir = None

# Load block image
block_img = pygame.image.load("block.png").convert_alpha()
block_img = pygame.transform.scale(block_img, (CELL_SIZE, CELL_SIZE))

# Grid
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Tetromino: O piece (no rotation for now)
tetromino = {
    "shape": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "x": 4,
    "y": 0
}

def draw_grid():
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(
                GRID_OFFSET_X + col * CELL_SIZE,
                GRID_OFFSET_Y + row * CELL_SIZE,
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)
            if grid[row][col]:
                screen.blit(block_img, rect.topleft)


def draw_tetromino():
    for dx, dy in tetromino["shape"]:
        x = GRID_OFFSET_X + (tetromino["x"] + dx) * CELL_SIZE
        y = GRID_OFFSET_Y + (tetromino["y"] + dy) * CELL_SIZE
        screen.blit(block_img, (x, y))


def valid_position(x_offset, y_offset):
    for dx, dy in tetromino["shape"]:
        x = tetromino["x"] + dx + x_offset
        y = tetromino["y"] + dy + y_offset
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return False
        if y >= 0 and grid[y][x]:
            return False
    return True


def lock_tetromino():
    for dx, dy in tetromino["shape"]:
        x = tetromino["x"] + dx
        y = tetromino["y"] + dy
        if 0 <= y < GRID_HEIGHT:
            grid[y][x] = True
    spawn_tetromino()


def spawn_tetromino():
    tetromino["x"] = 4
    tetromino["y"] = 0


# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000

    screen.fill("black")

    fall_timer += dt

    keys = pygame.key.get_pressed()

    # Handle DAS / ARR
    if keys[pygame.K_LEFT]:
        if move_dir != "left":
            move_dir = "left"
            key_hold["left"] = 0
        key_hold["left"] += dt
        if key_hold["left"] >= DAS:
            if valid_position(-1, 0):
                tetromino["x"] -= 1
            key_hold["left"] -= ARR
    elif keys[pygame.K_RIGHT]:
        if move_dir != "right":
            move_dir = "right"
            key_hold["right"] = 0
        key_hold["right"] += dt
        if key_hold["right"] >= DAS:
            if valid_position(1, 0):
                tetromino["x"] += 1
            key_hold["right"] -= ARR
    else:
        move_dir = None

    # Soft drop
    gravity_speed = 0.05 if keys[pygame.K_DOWN] else fall_interval
    if fall_timer >= gravity_speed:
        if valid_position(0, 1):
            tetromino["y"] += 1
        else:
            lock_tetromino()
        fall_timer = 0

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Instant single move input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and valid_position(-1, 0):
                tetromino["x"] -= 1
            if event.key == pygame.K_RIGHT and valid_position(1, 0):
                tetromino["x"] += 1
            if event.key == pygame.K_UP:
                # Placeholder for rotation logic
                pass

    # Draw
    draw_grid()
    draw_tetromino()

    pygame.display.flip()

pygame.quit()
