from threading import Thread, RLock
from time import sleep


class Grid:
    def __init__(self, n, verbose=False):
        self.n = n
        self.grid = [[None for i in range(n)] for j in range(n)]
        self.lock = RLock()
        self.verbose = verbose
        if verbose:
            print('Created grid of size', n)

    def is_empty(self, pos):
        return self.grid[pos[0]][pos[1]] is None

    def move(self, source, dest):
        """
        Move an agent in the grid
        :param source: source position
        :param dest: destination position
        :return: bool (True if done)
        """
        if self.is_valid_cell(dest) and self.is_empty(dest) \
                and (abs(source[0]-dest[0]) + abs(source[1]-dest[1])) <= 1:
            print('Invalid move', source, dest)
            return False

        agent = self.get(source)

        if self.verbose:
            print('Moving:', agent.id, 'from', source, 'to', dest)
        self.set(dest, agent)
        self.set(source, None)
        return True

    def add(self, agent):
        pos = agent.pos
        if not self.is_valid_cell(pos) or not self.is_empty(pos):
            print('Invalid position', agent.pos, 'for agent', agent.pos)
            return False

        self.set(pos, agent)
        return True

    def get(self, pos):
        return self.grid[pos[0]][pos[1]]

    def set(self, pos, a):
        self.grid[pos[0]][pos[1]] = a

    def is_valid_cell(self, pos):
        return pos[0]<self.n and pos[1]<self.n

    def __str__(self):
        s = []
        for row in self.grid:
            for cell in row:
                if cell is None:
                    s.append('.')
                else:
                    s.append(str(cell.id))
                s.append('\t')
            s.append('\n')
        return ''.join(s)


class Agent(Thread):

    def __init__(self, _id, pos, goal, grid):
        Thread.__init__(self)
        self.id = _id
        self.pos = pos
        self.goal = goal
        self.grid = grid
        self.stop = False

    def run(self):
        while not self.stop:
            if self.has_reached_goal():
                sleep(1)
            else:
                # Trying both axis
                for axis in range(2):
                    if self.pos[axis]-self.goal[axis] != 0:
                        stuck = not self.try_moving(axis=axis)

                        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    def try_moving(self, axis):
        # Chosing direction
        if self.pos[axis]-self.goal[axis] > 0:
            direction = -1
        else:
            direction = 1

        # Calculating destination
        if axis == 0:
            dest = (self.pos[0]+direction, self.pos[1])
        else:
            dest = (self.pos[0], self.pos[1]+direction)

        # Trying to move
        with self.grid.lock:
            return self.grid.move(self.pos, dest)

    def has_reached_goal(self):
        return self.pos == self.goal


g = Grid(5)
a1 = Agent(0, (0, 0), (1, 1), g)
a2 = Agent(1, (2, 2), (2, 1), g)
g.add(a1)
g.add(a2)

print(g)
