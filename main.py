import pygame
import random
from config import *
from config import KEYBINDS, TIMING
from tetromino import Tetromino, TETROMINOS
from grid import create_grid, clear_lines

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
        screen_x = GRID_OFFSET_X + (x - view_x) * CELL_SIZE * zoom
        screen_y = GRID_OFFSET_Y + (y - view_y) * CELL_SIZE * zoom
        rect = pygame.Rect(screen_x, screen_y, CELL_SIZE * zoom, CELL_SIZE * zoom)

        screen.blit(pygame.transform.scale(block_img, (int(CELL_SIZE * zoom), int(CELL_SIZE * zoom))), rect.topleft)

def draw_ghost(tetromino, grid):
    ghost = Tetromino(tetromino.type)
    ghost.x = tetromino.x
    ghost.y = tetromino.y
    ghost.rot = tetromino.rot

    while ghost.valid_at(ghost.x, ghost.y + 1, ghost.rot, grid):
        ghost.move(0, 1)

    for x, y in ghost.get_blocks():
        screen_x = GRID_OFFSET_X + (x - view_x) * CELL_SIZE * zoom
        screen_y = GRID_OFFSET_Y + (y - view_y) * CELL_SIZE * zoom
        rect = pygame.Rect(screen_x, screen_y, CELL_SIZE * zoom, CELL_SIZE * zoom)
        
       
        # Draw with transparency or grey
        ghost_img = block_img.copy()
        ghost_img.fill((255, 255, 255, 80), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(pygame.transform.scale(ghost_img, (int(CELL_SIZE * zoom), int(CELL_SIZE * zoom))), rect.topleft)


def draw_next(queue):
    label = pygame.font.SysFont("Arial", 24).render("Next:", True, (255, 255, 255))
    a = DISPLAY_X - 180
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

def draw_grid(screen, grid, view_x, view_y, zoom, selected_region):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            screen_x = GRID_OFFSET_X + (x - view_x) * CELL_SIZE * zoom
            screen_y = GRID_OFFSET_Y + (y - view_y) * CELL_SIZE * zoom
            rect = pygame.Rect(screen_x, screen_y, CELL_SIZE * zoom, CELL_SIZE * zoom)

            in_selected = False
            if selected_region:
                sx, sy = selected_region
                in_selected = sx <= x < sx + 10 and sy <= y < sy + 20

            # Color block based on selection
            if grid[y][x]:
                img = block_img.copy()
                if tetris_mode and not in_selected:
                    img.set_alpha(100)
                screen.blit(pygame.transform.scale(img, (int(CELL_SIZE * zoom), int(CELL_SIZE * zoom))), rect.topleft)
            else:
                pygame.draw.rect(screen, (40, 40, 40), rect, 1)

    # Optional: Draw outline of 10x20 region
    if selected_region:
        sx, sy = selected_region
        rect = pygame.Rect(
            GRID_OFFSET_X + (sx - view_x) * CELL_SIZE * zoom,
            GRID_OFFSET_Y + (sy - view_y) * CELL_SIZE * zoom,
            10 * CELL_SIZE * zoom,
            20 * CELL_SIZE * zoom
        )
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
                
pygame.init()
screen = pygame.display.set_mode((DISPLAY_X, DISPLAY_Y))
pygame.display.set_caption("minos")
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
DAS = TIMING["DAS"]
ARR = TIMING["ARR"]
SOFT_DROP_SPEED = TIMING["SOFT_DROP_SPEED"]
INFINITE_SOFT_DROP = TIMING["INFINITE_SOFT_DROP"]
key_hold_timer = {"left": 0, "right": 0}
key_held = {"left": False, "right": False}

# Soft drop
soft_drop_active = False
soft_drop_timer = 0

lock_delay = 0.5  # seconds
lock_timer = 0
grounded_last_frame = False

# Hold piece
hold_piece = None
can_hold = True

# Zoom
zoom = 1.0
view_x = 0.0  # In grid coordinates
view_y = 0.0

# Panning

panning = False
last_mouse_pos = (0, 0)

# Enable Tetris

tetris_mode = False
selected_region = None  # (x, y) top-left of 10×20 field

# Offset all tetromino logic by (selected_region or (0, 0))
tx, ty = selected_region if selected_region else (0, 0)

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
        if INFINITE_SOFT_DROP:
            while tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot, grid):
                tetromino.move(0, 1)
            fall_timer = 0
            lock_timer = 0
            soft_drop_active = False
        else:
            soft_drop_timer += dt
            if soft_drop_timer >= SOFT_DROP_SPEED:
                if tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot, grid):
                    tetromino.move(0, 1)
                    lock_timer = 0
                soft_drop_timer = 0
    else:
        if not grounded:
            if fall_timer >= fall_interval:
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
                fall_timer = 0  # reset fall timer after locking
    
    # Reset lock timer on manual movement
    if grounded_last_frame and not grounded:
        lock_timer = 0
    grounded_last_frame = grounded
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == KEYBINDS["move_left"]:
                key_held["left"] = True
                key_hold_timer["left"] = 0
                if tetromino.valid_at(tetromino.x - 1, tetromino.y, tetromino.rot, grid):
                    tetromino.move(-1, 0)
                    lock_timer = 0
            elif event.key == KEYBINDS["move_right"]:
                key_held["right"] = True
                key_hold_timer["right"] = 0
                if tetromino.valid_at(tetromino.x + 1, tetromino.y, tetromino.rot, grid):
                    tetromino.move(1, 0)
                    lock_timer = 0
            elif event.key == KEYBINDS["soft_drop"]:
                soft_drop_active = True
            elif event.key == KEYBINDS["rotate_cw"]:
                tetromino.rotate(1, grid)
                lock_timer = 0
            elif event.key == KEYBINDS["rotate_ccw"]:
                tetromino.rotate(-1, grid)
                lock_timer = 0
            elif event.key == KEYBINDS["rotate_180"]:
                tetromino.rotate(1, grid, angle=180)
                lock_timer = 0
            elif event.key == KEYBINDS["hard_drop"]:
                # Hard drop
                while tetromino.valid_at(tetromino.x, tetromino.y + 1, tetromino.rot, grid):
                    tetromino.move(0, 1)
                tetromino.lock(grid)
                grid, cleared = clear_lines(grid)
                tetromino = spawn_piece()
                can_hold = True
                fall_timer = 0
                lock_timer = 0
            elif event.key == KEYBINDS["hold"]:
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
            if event.key == KEYBINDS["move_left"]:
                key_held["left"] = False
            elif event.key == KEYBINDS["move_right"]:
                key_held["right"] = False
            elif event.key == KEYBINDS["soft_drop"]:
                soft_drop_active = False
        
        elif event.type == pygame.MOUSEWHEEL:
            old_zoom = zoom
            zoom *= 1.1 if event.y > 0 else 0.9
            zoom = max(0.25, min(4.0, zoom))

            # Zoom around mouse position
            mx, my = pygame.mouse.get_pos()
            gx = view_x + (mx - GRID_OFFSET_X) / (CELL_SIZE * old_zoom)
            gy = view_y + (my - GRID_OFFSET_Y) / (CELL_SIZE * old_zoom)
            view_x = gx - (mx - GRID_OFFSET_X) / (CELL_SIZE * zoom)
            view_y = gy - (my - GRID_OFFSET_Y) / (CELL_SIZE * zoom)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            panning = True
            last_mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            panning = False

        if event.type == pygame.MOUSEMOTION and panning:
            mx, my = pygame.mouse.get_pos()
            dx = (last_mouse_pos[0] - mx) / (CELL_SIZE * zoom)
            dy = (last_mouse_pos[1] - my) / (CELL_SIZE * zoom)
            view_x += dx
            view_y += dy
            last_mouse_pos = (mx, my)

        if tetris_mode and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            gx = int(view_x + (mx - GRID_OFFSET_X) / (CELL_SIZE * zoom))
            gy = int(view_y + (my - GRID_OFFSET_Y) / (CELL_SIZE * zoom))
            if 0 <= gx <= GRID_WIDTH - 10 and 0 <= gy <= GRID_HEIGHT - 20:
                selected_region = (gx, gy)



        


    screen.fill("black")
    draw_grid(screen, grid, view_x, view_y, zoom, selected_region)
    draw_ghost(tetromino, grid)
    draw_tetromino(tetromino)
    draw_next(queue)
    draw_hold(hold_piece)
    pygame.display.flip()

pygame.quit()
