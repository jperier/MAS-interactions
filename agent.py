from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder

from threading import Thread, RLock
from time import sleep
import random


class Agent(Thread):

    def __init__(self, _id, pos, goal, grid, friendliness=1, laziness=0):
        Thread.__init__(self, name='Agent_'+str(_id)+'_Thread')
        self.id = _id
        self.pos = pos
        self.goal = goal
        self.grid = grid
        self.stop = False
        self.delay = 3  #random.uniform(0.1, 0.3)

    def run(self):
        while not self.stop:
            if self.has_reached_goal():
                sleep(0.5)
            else:
                if not self.try_moving():
                    sleep(self.delay)

    def try_moving(self):
        # Choosing axis
        axis = random.randint(0, 1)
        if abs(self.pos[axis]-self.goal[axis]) == 0:
            axis = 1 - axis     # Changing axis

        dest = self.find_destination(axis)

        # Trying to move
        with self.grid.lock:

            moved, blocking_agent = self.grid.move(self.pos, dest)

            if moved:
                self.pos = dest
                return True

            # If not possible, trying other axis    TODO: marche pas correctement
            axis = 1 - axis
            if abs(self.pos[axis] - self.goal[axis]) == 0:
                dest = self.find_destination(axis)
                moved, blocking_agent = self.grid.move(self.pos, dest)
                if moved:
                    self.pos = dest
                    return True

            # TODO : add option to be lazy and not wanting to go-round
            # If the other axis is not interesting, trying to go-round
            elif self.try_go_round():
                return True
            print('Agent', self.id, 'blocked !', self.pos)
            # TODO : negociate
            return False

    def find_destination(self, axis):
        # Choosing direction
        if self.pos[axis]-self.goal[axis] > 0:
            direction = -1
        else:
            direction = 1

        # Calculating destination for the next move
        if axis == 0:
            dest = (self.pos[0]+direction, self.pos[1])
        else:
            dest = (self.pos[0], self.pos[1]+direction)

        return dest

    def try_go_round(self):
        # Finding best path with A* if possible
        path_grid = PathGrid(matrix=self.grid.to_one_and_zeros_t())
        start = path_grid.node(*self.pos)
        end = path_grid.node(*self.goal)
        finder = AStarFinder()

        path, _ = finder.find_path(start, end, path_grid)

        # If not possible, return False
        if len(path) == 0:
            return False
        else:
            # Transposing indices
            # path = [(x[1], x[0]) for x in path]
            print('Agent', self.id, 'going round:', path)
            # Moving step by step
            last_cell = self.pos
            for next_cell in path[1:]:
                assert self.grid.move(last_cell, next_cell)
                last_cell = next_cell

        self.pos = self.goal
        assert self.grid.get(self.goal) == self
        return True

    def has_reached_goal(self):
        return self.pos == self.goal
