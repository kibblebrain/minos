import pygame
import random
from config import *
from tetromino import Tetromino, TETROMINOS
from grid import create_grid, draw_grid, clear_lines

def refill_bag():
    types = list(TETROMINOS.keys())
    random.shuffle(types)
    bag.extend(types)

def spawn_piece():
    # Ensure queue has enough pieces
    while len(queue) < QUEUE_SIZE:
        if not bag:
            refill_bag()
        queue.append(bag.pop())
    return Tetromino(queue.pop(0))

def draw_tetromino(tetromino):
    for x, y in tetromino.get_blocks():
        px = GRID_OFFSET_X + x * CELL_SIZE
        py = GRID_OFFSET_Y + y * CELL_SIZE
        screen.blit(block_img, (px, py))

def draw_ghost(tetromino, grid):
    ghost = Tetromino(tetromino.type)
    ghost.x = tetromino.x
    ghost.y = tetromino.y
    ghost.rot = tetromino.rot

    while ghost.valid_at(ghost.x, ghost.y + 1, ghost.rot, grid):
        ghost.move(0, 1)

    for x, y in ghost.get_blocks():
        px = GRID_OFFSET_X + x * CELL_SIZE
        py = GRID_OFFSET_Y + y * CELL_SIZE
        # Draw with transparency or grey
        ghost_img = block_img.copy()
        ghost_img.fill((255, 255, 255, 80), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(ghost_img, (px, py))

def draw_next(queue):
    label = pygame.font.SysFont("Arial", 24).render("Next:", True, (255, 255, 255))
    a = GRID_OFFSET_X + (GRID_WIDTH+2)*CELL_SIZE
    screen.blit(label, (a, 50))
    for i in range(min(5, len(queue))):
        shape = TETROMINOS[queue[i]][0]
        for dx, dy in shape:
            px = a + dx * CELL_SIZE
            py = 80 + i * 3 * CELL_SIZE + dy * CELL_SIZE
            screen.blit(block_img, (px, py))

def draw_hold(hold_piece):
    label = pygame.font.SysFont("Arial", 24).render("Hold:", True, (255, 255, 255))
    screen.blit(label, (50, 50))
    if hold_piece:
        shape = TETROMINOS[hold_piece][0]
        for dx, dy in shape:
            px = 60 + dx * CELL_SIZE
            py = 80 + dy * CELL_SIZE
            screen.blit(block_img, (px, py))

pygame.init()
screen = pygame.display.set_mode((720, 720))
pygame.display.set_caption("Tetris Engine")
clock = pygame.time.Clock()

block_img = pygame.image.load("assets/block.png").convert_alpha()
block_img = pygame.transform.scale(block_img, (CELL_SIZE, CELL_SIZE))

grid = create_grid()
bag = []
queue = [] # Next pieces
QUEUE_SIZE = 6  # 5 preview + 1 current
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

# Hold piece
hold_piece = None
can_hold = True

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
                while tetromino.valid_at(tetromino.x + dx, tetromino.y, tetromino.rot, grid):
                    tetromino.move(dx, 0)

    grounded = not tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot, grid)

    # Infinite soft drop logic
    if soft_drop_active:
        if not grounded:
            tetromino.move(0, 1)
            fall_timer = 0
            lock_timer = 0
        else:
            lock_timer += dt
            if lock_timer >= lock_delay:
                tetromino.lock(grid)
                grid, cleared = clear_lines(grid)
                tetromino = spawn_piece()
                can_hold = True
                lock_timer = 0
    else:
        if fall_timer >= fall_interval:
            if not grounded:
                tetromino.move(0, 1)
                lock_timer = 0
            else:
                lock_timer += fall_timer
                if lock_timer >= lock_delay:
                    tetromino.lock(grid)
                    grid, cleared = clear_lines(grid)
                    tetromino = spawn_piece()
                    can_hold = True
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
                if tetromino.valid_at(tetromino.x - 1, tetromino.y, tetromino.rot, grid):
                    tetromino.move(-1, 0)
                    lock_timer = 0
            elif event.key == pygame.K_RIGHT:
                key_held["right"] = True
                key_hold_timer["right"] = 0
                if tetromino.valid_at(tetromino.x + 1, tetromino.y, tetromino.rot, grid):
                    tetromino.move(1, 0)
                    lock_timer = 0
            elif event.key == pygame.K_DOWN:
                soft_drop_active = True
            elif event.key == pygame.K_UP:
                tetromino.rotate(1, grid)
                lock_timer = 0
            elif event.key == pygame.K_z:
                tetromino.rotate(-1, grid)
                lock_timer = 0
            elif event.key == pygame.K_SPACE:
                # Hard drop
                while tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot, grid):
                    tetromino.move(0, 1)
                tetromino.lock(grid)
                grid, cleared = clear_lines(grid)
                tetromino = spawn_piece()
                can_hold = True
                fall_timer = 0
                lock_timer = 0
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                if can_hold:
                    if hold_piece is None:
                        hold_piece = tetromino.type
                        tetromino = spawn_piece()
                    else:
                        hold_piece, tetromino = tetromino.type, Tetromino(hold_piece)
                    can_hold = False
                    fall_timer = 0
                    lock_timer = 0


        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                key_held["left"] = False
            elif event.key == pygame.K_RIGHT:
                key_held["right"] = False
            elif event.key == pygame.K_DOWN:
                soft_drop_active = False
        


    screen.fill("black")
    draw_grid(screen, grid, block_img)
    draw_ghost(tetromino, grid)
    draw_tetromino(tetromino)
    draw_next(queue)
    draw_hold(hold_piece)
    pygame.display.flip()

pygame.quit()
