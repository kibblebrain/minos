import random
from config import TETROMINO_TYPES, GRID_WIDTH, GRID_HEIGHT

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

    def rotate(self, direction, grid):
        old_rot = self.rot
        new_rot = (self.rot + direction) % 4
        kicks = KICK_TABLE.get((old_rot, new_rot), [(0, 0)])
        for ox, oy in kicks:
            if self.valid_at(self.x + ox, self.y + oy, new_rot, grid):
                self.rot = new_rot
                self.x += ox
                self.y += oy
                return

    def valid_at(self, x, y, rot, grid):
        for dx, dy in self.shape[rot]:
            tx = x + dx
            ty = y + dy
            if tx < 0 or tx >= GRID_WIDTH or ty >= GRID_HEIGHT:
                return False
            if ty >= 0 and grid[ty][tx]:
                return False
        return True

    def valid(self, grid):
        return self.valid_at(self.x, self.y, self.rot, grid)

    def lock(self, grid):
        for x, y in self.get_blocks():
            if 0 <= y < GRID_HEIGHT:
                grid[y][x] = True