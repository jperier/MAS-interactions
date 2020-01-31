from agent import Agent
from grid import Grid
from random import randint
from time import sleep
from mailbox import MailBox


N_GRID = 3
N_AGENTS = 4
VERBOSE = True
MAX_ITER = 30
REFRESH_TIME = 0.1


def rand_pos(domain):
    return randint(*domain), randint(*domain)


if __name__ == '__main__':
    assert N_AGENTS < N_GRID**2

    # Creating grid
    grid = Grid(N_GRID, verbose=VERBOSE)
    mailbox = MailBox()

    # Creating agents
    agents = []

    agents.append(Agent(0, (0, 0), (2, 2), grid, mailbox))
    agents.append(Agent(1, (1, 0), (1, 0), grid, mailbox))
    agents.append(Agent(2, (0, 1), (0, 1), grid, mailbox))
    for agent in agents:
        assert grid.add(agent)

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

        i += 1

    # Finishing agents
    for a in agents:
        a.stop = True
        a.join()

print('Fini')
