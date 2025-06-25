import pygame

CELL_SIZE = 32
GRID_WIDTH = 64
GRID_HEIGHT = 64
GRID_OFFSET_X = 200
GRID_OFFSET_Y = 40
DISPLAY_X = 1920
DISPLAY_Y = 1080

DAS = 0.15
ARR = 0
LOCK_DELAY = 0.5
FALL_INTERVAL = 0.5

TETROMINO_TYPES = ["I", "O", "T", "S", "Z", "J", "L"]

KEYBINDS = {
    "move_left": pygame.K_LEFT,
    "move_right": pygame.K_RIGHT,
    "soft_drop": pygame.K_DOWN,
    "hard_drop": pygame.K_SPACE,
    "rotate_cw": pygame.K_e,
    "rotate_ccw": pygame.K_w,
    "rotate_180": pygame.K_a,
    "hold": pygame.K_LSHIFT,
    "pause": pygame.K_ESCAPE,
}

# Timing in seconds
TIMING = {
    "DAS": 0.15,           # Delay Auto Shift
    "ARR": 0.0,            # Auto Repeat Rate; 0 = instant
    "SOFT_DROP_SPEED": 0.02, # seconds per soft drop step
    "INFINITE_SOFT_DROP": True
}
