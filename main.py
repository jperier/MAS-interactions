import sys

from mailbox import MailBox
from agent import Agent
from grid import Grid
from random import randint
from time import sleep


N_GRID = 5
N_AGENTS = 7
VERBOSE = True
MAX_ITER = 300
REFRESH_TIME = 0.1


def rand_pos(domain):
    return randint(*domain), randint(*domain)


if __name__ == '__main__':
    assert N_AGENTS < N_GRID**2

    grid = Grid(N_GRID, verbose=VERBOSE)
    mailbox = MailBox()

    # Creating agents
    agents = []
    goals = []
    domain = (0, N_GRID-1)
    for i in range(N_AGENTS):
        pos = rand_pos(domain)
        goal = rand_pos(domain)
        while pos == goal or not grid.is_empty(pos) or goal in goals:
            pos = rand_pos(domain)
            goal = rand_pos(domain)

        agent = Agent(i, pos, goal, grid, mailbox)
        if grid.add(agent):
            agents.append(agent)
            goals.append(goal)
            if VERBOSE:
                print('Agent', i, 'crée à la position', pos, 'avec objectif', goal)

    print(grid)

    # Starting agents
    for a in agents:
        a.start()

    # Looping until agents are done or MAX_ITER is reached
    nb_completed_goal = 0
    i = 0
    while nb_completed_goal < N_AGENTS and i <= MAX_ITER:

        sleep(REFRESH_TIME)

        nb_completed_goal = 0
        for a in agents:
            if a.has_reached_goal():
                nb_completed_goal += 1

        # with grid.lock:
        #     print(grid)
        i += 1

    # Finishing agents
    for a in agents:
        a.stop = True
        a.join()

print('Fini')
