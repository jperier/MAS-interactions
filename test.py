from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

matrix = [
  [1, 1, 1],
  [1, 0, 1],
  [0, 1, 1]
]

grid = Grid(matrix=matrix)

start = grid.node(0, 0)
end = grid.node(2, 1)

finder = AStarFinder()#diagonal_movement=DiagonalMovement.always)
path, runs = finder.find_path(start, end, grid)

print('operations:', runs, 'path length:', len(path))

print(grid.grid_str(path=path, start=start, end=end))

print(path)


# +---+
# |sxx|
# | #e|
# |#  |
# +---+
# [(0, 0), (1, 0), (2, 0), (2, 1)]