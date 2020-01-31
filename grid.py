from threading import Lock


def manathan_dist(a, b):
    return abs(a.pos[0]-b.pos[0]) + abs(a.pos[1]-b.pos[1])


class Grid:
    def __init__(self, n, verbose=False):
        self.n = n
        self.grid = [[None for i in range(n)] for j in range(n)]
        self.lock = Lock()
        self.agents = []
        self.goals = {}
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
        :return: (True, None) if done else (False, Agent blocking the way)
        """
        # Verifying if the move is valid
        if not self.is_valid_cell(dest):
            if self.verbose: print('Invalid destination cell', source, '->', dest, 'agent', self.get(source).id)
            return False

        elif not self.is_empty(dest):
            if self.verbose: print('Destination cell not empty', source, '->', dest, 'agent', self.get(source).id)
            return False

        elif not (abs(source[0]-dest[0]) + abs(source[1]-dest[1])) == 1:
            if self.verbose: print('Moving distance != 1', source, '->', dest, 'agent', self.get(source).id)
            return False

        # Moving agent
        agent = self.get(source)
        assert agent is not None

        self.set(dest, agent)
        self.set(source, None)
        if self.verbose:
            print('Moving:', agent.id, 'from', source, 'to', dest)
            print(self)
        return True

    def add(self, agent):
        pos = agent.pos
        if not self.is_valid_cell(pos) or not self.is_empty(pos):
            print('Invalid position', agent.pos, 'for agent', agent.pos)
            return False

        self.set(pos, agent)
        self.agents.append(agent)
        self.goals[agent.goal] = str(agent.id)
        return True

    def get(self, pos):
        return self.grid[pos[0]][pos[1]]

    def set(self, pos, a):
        self.grid[pos[0]][pos[1]] = a

    def is_valid_cell(self, pos):
        return pos[0]<self.n and pos[1]<self.n

    def to_one_and_zeros_t(self, ignore=None):
        """
        Transposes and converts the grid in a 1 and 0 2D-list, 1 represents the free cells and 0 the obstacles
        :param: ignore : an agent to ignore (return the grid as if he was not in it)
        :return: 2D list
        """
        res = [[None for i in range(self.n)] for j in range(self.n)]

        for i in range(self.n):
            for j in range(self.n):
                res[j][i] = 1 if self.grid[i][j] in (None, ignore) else 0
        return res

    def to_one_and_zeros_t_except_each(self, agent_asking, max_dist=4):
        """
        Transposes and converts the grid in a 1 and 0 2D-list, 1 represents the free cells and 0 the obstacles
        :return: 3D list, tuple( agent, list of 2D list ignoring this agent)
        """
        for a in self.agents:
            if not agent_asking == a and manathan_dist(a, agent_asking) <= max_dist:
                yield a, self.to_one_and_zeros_t(ignore=a)

    def get_free_adjacent_cells(self, pos):
        res = []
        if pos[0] < self.n - 1:
            c = (pos[0]+1, pos[1])
            if self.is_empty(c):
                res.append(c)
        if pos[1] < self.n - 1:
            c = (pos[0], pos[1] + 1)
            if self.is_empty(c):
                res.append(c)
        if pos[0] > 0:
            c = (pos[0]-1, pos[1])
            if self.is_empty(c):
                res.append(c)
        if pos[1] > 0:
            c = (pos[0], pos[1]-1)
            if self.is_empty(c):
                res.append(c)
        return res

    def __str__(self):
        s = []
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell is not None:
                    s.append('A'+str(cell.id))
                else:
                    if (i, j) in self.goals.keys():
                        s.append(f'({self.goals[(i,j)]})')
                    else:
                        s.append('.')
                s.append('\t\t')
            s.append('\n\n')
        return ''.join(s)
