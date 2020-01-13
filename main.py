import sys

from classes import Agent, Grid
from random import randint


N_GRID = 5
N_AGENTS = 1
VERBOSE = True


def sprint(s, end='\n'):
    sys.stdout.write(str(s)+end)
    sys.stdout.flush()


def rand_pos(domain):
    return randint(*domain), randint(*domain)


if __name__ == '__main__':
    assert N_AGENTS < N_GRID

    # Creating grid
    grid = Grid(N_GRID, verbose=VERBOSE)

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

        agent = Agent(i, pos, goal, grid)
        if grid.add(agent):
            agents.append(agent)
            goals.append(goal)
            if VERBOSE:
                print('Agent', i, 'crée à la position', pos, 'avec objectif', goal)

    # Starting agents
    for a in agents:
        a.start()

    # TODO: Observer/Observable
    # https://stackoverflow.com/questions/13528213/observer-observable-classes-in-python
    # https://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips (plutot celle ci a priori)

    # Finishing agents
    for a in agents:
        a.stop = True
        a.join()

print('Fini')
