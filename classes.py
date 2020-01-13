from threading import Thread, RLock


class Grid:
    def __init__(self, n, verbose=False):
        self.n = n
        self.grid = [[None]*n]*n
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
        if self.is_valid_cell(dest) and not self.is_empty(dest) \
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
        if self.is_valid_cell(pos) and not self.is_empty(pos):
            print('Invalid position', agent.pos, 'for agent', agent.pos)
            return False

        self.set(pos, agent)
        return True

    def get(self, pos):
        return self.grid[pos[0]][pos[1]]

    def set(self, pos, val):
        self.grid[pos[0]][pos[1]] = val

    def is_valid_cell(self, pos):
        return pos[0]<self.n and pos[1]<self.n


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
            if self.pos != self.goal:
                for axis in range(2):
                    if self.pos[axis]-self.goal[axis] != 0:
                        stuck = not self.try_moving(axis=axis)

    def try_moving(self, axis):
        if self.pos[axis]-self.goal[axis] > 0:
            direction = -1
        else:
            direction = 1

        if axis == 0:
            dest = (self.pos[0]+direction, self.pos[1])
        else:
            dest = (self.pos[0], self.pos[1]+direction)

        with self.grid.lock:
            return self.grid.move(self.pos, dest)
