from threading import RLock


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

    def go_round(self, source, dest):
        pass

    def move(self, source, dest):
        """
        Move an agent in the grid
        :param source: source position
        :param dest: destination position
        :return: (True, None) if done else (False, Agent blocking the way)
        """
        # Verifying if the move is valid
        if not self.is_valid_cell(dest):
            if self.verbose: print('Invalid destination cell', source, '->', dest)
            return False, None

        elif not self.is_empty(dest):
            if self.verbose: print('Destination cell not empty', source, '->', dest)
            return False, self.get(dest).id

        elif not (abs(source[0]-dest[0]) + abs(source[1]-dest[1])) == 1:
            if self.verbose: print('Moving distance != 1', source, '->', dest)
            return False, None

        # Moving agent
        agent = self.get(source)
        assert agent is not None

        self.set(dest, agent)
        self.set(source, None)
        if self.verbose:
            print('Moving:', agent.id, 'from', source, 'to', dest)
            print(self)
        return True, None

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

    def to_one_and_zeros_t(self):
        """
        Transposes and converts the grid in a 1 and 0 2D-list, 1 represents the free cells and 0 the obstacles
        :return: 2D list
        """
        res = [[None for i in range(self.n)] for j in range(self.n)]

        for i in range(self.n):
            for j in range(self.n):
                res[j][i] = 1 if self.grid[i][j] is None else 0
        return res

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
