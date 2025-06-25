import random
from config import TETROMINO_TYPES, GRID_WIDTH, GRID_HEIGHT
from srs import JLSTZ_KICKS, I_KICKS

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

class Tetromino:
    def __init__(self, type_):
        self.type = type_
        self.rot = 0
        self.x = GRID_WIDTH//2 - 2 if type_ != "I" else GRID_WIDTH//2 - 3
        self.y = 0
        self.shape = TETROMINOS[type_]

    def get_blocks(self):
        return [(self.x + dx, self.y + dy) for dx, dy in self.shape[self.rot]]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self, direction, grid, angle=90):
        old_rot = self.rot
        if angle == 180:
            new_rot = (self.rot + 2) % 4
        else:
            new_rot = (self.rot + direction) % 4

        if self.type == "I":
            kicks = I_KICKS.get((old_rot, new_rot), [(0, 0)])
        elif self.type == "O":
            # O piece doesn't rotate around origin (no kicks really)
            self.rot = new_rot
            return
        else:
            kicks = JLSTZ_KICKS.get((old_rot, new_rot), [(0, 0)])

        for ox, oy in kicks:
            nx = self.x + ox
            ny = self.y + oy
            if self.valid_at(nx, ny, new_rot, grid):
                self.rot = new_rot
                self.x = nx
                self.y = ny
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