from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder

from collections import deque
from threading import Thread, Lock
from time import sleep
import random


WAIT_FOR_RESPONSES = 0.5
MSG_SCOPE = 4
WAIT_FOR_CONFIRM = 4
print_lock = Lock()


class Agent(Thread):

    def __init__(self, _id, pos, goal, grid, mailbox, timeout=0.2, friendliness=1, laziness=0, dumb=False):
        Thread.__init__(self, name='Agent_'+str(_id)+'_Thread')
        self.id = _id
        self.pos = pos
        self.goal = goal
        self.grid = grid
        self.mailbox = mailbox
        self.timeout = timeout
        self.friendliness = friendliness
        self.laziness = laziness
        self.dumb = dumb
        self.stop = False
        self.delay = random.uniform(0.1, 0.3)

    def run(self):
        while not self.stop:
            # Checking mails
            self.check_mails()

            if self.has_reached_goal():
                sleep(0.5)
            # Acting
            else:
                if self.grid.lock.acquire():

                    path = self.find_path(self.goal)

                    # If possible we move
                    if len(path) > 0:
                        assert self.grid.move(self.pos, path[1])
                        self.pos = path[1]

                    # Else try to negotiate
                    else:
                        # Looking which agent could give way in the line of sight
                        has_send_req = False
                        for agent, matrix in self.grid.to_one_and_zeros_t_except_each(self, max_dist=MSG_SCOPE):
                            path_to_free = self.find_path(self.goal, matrix=matrix)
                            if len(path_to_free) > 1:
                                with self.mailbox.lock:
                                    self.mailbox.request(self, agent, path_to_free)
                                    has_send_req = True
                                    print(self.id, "sending request to", agent, path_to_free)

                        if has_send_req:
                            sleep(WAIT_FOR_RESPONSES)

                            # Looking for responses and acting
                            with self.mailbox.lock:
                                responses = self.mailbox.check_responses(self)
                                if len(responses) > 0:
                                    conv = {'cost': float('inf'), 'response': False}
                                    for c in responses:
                                        if c['response'] and c['cost'] < conv['cost']:
                                            conv = c
                                    if conv['response']:
                                        self.mailbox.confirm_choice(self, conv)
                                        self.follow_path(conv['path_to_free'][:(conv['cost']//2+2)])
                                        # waits for the other agent to regain its position, if necessary
                                        self.mailbox.done(conv, wait=True, remove_topic=True)
                    self.grid.lock.release()

    def check_mails(self):
        if self.mailbox.lock.acquire(timeout=1):
            conv = self.mailbox.check_requests(self)
            self.mailbox.lock.release()
            # with print_lock:
            #     # print(self.id, "Checked requests", conv)

            if conv is not None:
                # Responding in the conversation
                conv['response'], conv['path_to_follow'], conv['return_path'] = self.will_give_way(conv['path_to_free'])
                conv['cost'] = len(conv['path_to_follow'])
                # Wait for confirm and act if confirmed
                if self.mailbox.wait_for_confirm(conv, timeout=WAIT_FOR_CONFIRM):
                    # We have the lock on the grid bc the agent asking has it and waits for response
                    self.follow_path(conv['path_to_follow'])
                    self.mailbox.done(conv, wait=True)  # waits for the first agent to move
                    self.follow_path(conv['return_path'])
                    self.mailbox.done(conv)

    def find_path(self, dest, matrix=None):
        if matrix is None:
            matrix = self.grid.to_one_and_zeros_t()
        # Finding best path with A* if possible
        path_grid = PathGrid(matrix=matrix)
        start = path_grid.node(*self.pos)
        end = path_grid.node(*dest)
        finder = AStarFinder()

        path, _ = finder.find_path(start, end, path_grid)
        return path

    def follow_path(self, path):
        # Moving step by step
        last_cell = self.pos
        for next_cell in path[1:]:
            assert self.grid.move(last_cell, next_cell)
            last_cell = next_cell
        if len(path) > 0:
            self.pos = path[-1]

    def has_reached_goal(self):
        return self.pos == self.goal

    def will_give_way(self, path_to_free, max_cost=4):
        """
        If possible, will give way to another agent that wants to follow path_to_free.
        Return the path that this agent will need to follow if he wants to go back to its position, empty list if
        it has no interest in returning back.
        :param max_cost: the max amount of steps to follow
        :param path_to_free:
        :return: tuple(True if gave way else False, reverse_path)
        """
        # TODO: not wanting to give way ?
        # TODO look if interesting to return
        path_to_follow = self.find_path_to_give_way(path_to_free, max_cost=max_cost)
        if self.has_reached_goal():
            return_path = list(reversed(path_to_follow))
        else:
            return_path = []
        return len(path_to_follow) > 0, path_to_follow, return_path

    def find_path_to_give_way(self, path_to_free, max_cost):
        """ Breadth First Search to find the shortest path to free path_to_free"""
        visited, queue = set(), deque([self.pos])
        approx_cost = 0

        while queue and approx_cost < max_cost:
            approx_cost += 0.5
            vertex = queue.popleft()
            for cell in self.grid.get_free_adjacent_cells(vertex):
                if cell not in visited:
                    if cell in path_to_free:
                        visited.add(cell)
                        queue.append(cell)
                    else:
                        return self.find_path(cell)
        return []
