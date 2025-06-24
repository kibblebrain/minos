import pygame
import random

pygame.init()
screen = pygame.display.set_mode((640, 720))
pygame.display.set_caption("Tetris Engine")

clock = pygame.time.Clock()

# Grid
CELL_SIZE = 32
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFFSET_X = 100
GRID_OFFSET_Y = 40

# Load block image
block_img = pygame.image.load("block.png").convert_alpha()
block_img = pygame.transform.scale(block_img, (CELL_SIZE, CELL_SIZE))

# Define tetromino shapes and rotations
TETROMINOS = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)]
    ] * 4,
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

# Basic SRS kick table (non-I pieces)
KICK_TABLE = {
    (0, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (1, 0): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
    (3, 2): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (0, 3): [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
}

# Grid
grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE,
                               GRID_OFFSET_Y + y * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)
            if grid[y][x]:
                screen.blit(block_img, rect.topleft)


class Tetromino:
    def __init__(self, type_):
        self.type = type_
        self.rot = 0
        self.x = 3 if type_ != "I" else 2
        self.y = 0
        self.shape = TETROMINOS[type_]

    def get_blocks(self):
        return [(self.x + dx, self.y + dy) for dx, dy in self.shape[self.rot]]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self, direction):
        old_rot = self.rot
        new_rot = (self.rot + direction) % 4
        kicks = KICK_TABLE.get((old_rot, new_rot), [(0, 0)])
        for ox, oy in kicks:
            if self.valid_at(self.x + ox, self.y + oy, new_rot):
                self.rot = new_rot
                self.x += ox
                self.y += oy
                return

    def valid_at(self, x, y, rot):
        for dx, dy in self.shape[rot]:
            tx = x + dx
            ty = y + dy
            if tx < 0 or tx >= GRID_WIDTH or ty >= GRID_HEIGHT:
                return False
            if ty >= 0 and grid[ty][tx]:
                return False
        return True

    def lock(self):
        for x, y in self.get_blocks():
            if 0 <= y < GRID_HEIGHT:
                grid[y][x] = True


def draw_tetromino(tetromino):
    for x, y in tetromino.get_blocks():
        px = GRID_OFFSET_X + x * CELL_SIZE
        py = GRID_OFFSET_Y + y * CELL_SIZE
        screen.blit(block_img, (px, py))


def spawn_piece():
    return Tetromino(random.choice(bag.pop() if bag else refill_bag()))


def refill_bag():
    types = list(TETROMINOS.keys())
    random.shuffle(types)
    bag.extend(types)
    return bag.pop()


# Game state
bag = []
tetromino = spawn_piece()
fall_timer = 0
fall_interval = 0.5

# DAS/ARR settings
DAS = 0.15
ARR = 0  # Instant repeat
key_hold_timer = {"left": 0, "right": 0}
key_held = {"left": False, "right": False}

# Soft drop
soft_drop_active = False

lock_delay = 0.5  # seconds
lock_timer = 0
grounded_last_frame = False

running = True
while running:
    dt = clock.tick(60) / 1000
    fall_timer += dt

    # DAS + Instant ARR logic
    for direction in ("left", "right"):
        if key_held[direction]:
            key_hold_timer[direction] += dt
            if key_hold_timer[direction] >= DAS:
                dx = -1 if direction == "left" else 1
                while tetromino.valid_at(tetromino.x + dx, tetromino.y, tetromino.rot):
                    tetromino.move(dx, 0)

    grounded = not tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot)

    # Infinite soft drop logic
    if soft_drop_active:
        if not grounded:
            tetromino.move(0, 1)
            fall_timer = 0
            lock_timer = 0
        else:
            lock_timer += dt
            if lock_timer >= lock_delay:
                tetromino.lock()
                tetromino = spawn_piece()
                lock_timer = 0
    else:
        if fall_timer >= fall_interval:
            if not grounded:
                tetromino.move(0, 1)
                lock_timer = 0
            else:
                lock_timer += fall_timer
                if lock_timer >= lock_delay:
                    tetromino.lock()
                    tetromino = spawn_piece()
                    lock_timer = 0
            fall_timer = 0

    # Reset lock timer on manual movement
    if grounded_last_frame and not grounded:
        lock_timer = 0
    grounded_last_frame = grounded

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                key_held["left"] = True
                key_hold_timer["left"] = 0
                if tetromino.valid_at(tetromino.x - 1, tetromino.y, tetromino.rot):
                    tetromino.move(-1, 0)
                    lock_timer = 0
            elif event.key == pygame.K_RIGHT:
                key_held["right"] = True
                key_hold_timer["right"] = 0
                if tetromino.valid_at(tetromino.x + 1, tetromino.y, tetromino.rot):
                    tetromino.move(1, 0)
                    lock_timer = 0
            elif event.key == pygame.K_DOWN:
                soft_drop_active = True
            elif event.key == pygame.K_UP:
                tetromino.rotate(1)
                lock_timer = 0
            elif event.key == pygame.K_z:
                tetromino.rotate(-1)
                lock_timer = 0

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                key_held["left"] = False
            elif event.key == pygame.K_RIGHT:
                key_held["right"] = False
            elif event.key == pygame.K_DOWN:
                soft_drop_active = False

    screen.fill("black")
    draw_grid()
    draw_tetromino(tetromino)
    pygame.display.flip()

pygame.quit()
