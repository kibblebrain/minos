import pygame
from config import *

def clear_lines(grid):
    new_grid = []
    lines_cleared = 0
    for row in grid:
        if all(cell for cell in row):
            lines_cleared += 1
        else:
            new_grid.append(row)
    for _ in range(lines_cleared):
        new_grid.insert(0, [None] * GRID_WIDTH)
    return new_grid, lines_cleared

def create_grid():
    return [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

