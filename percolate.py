# The following generates an nD porous environment by randomly filling spaces
# based on some density. For the 2D case, the user can flood the environment to
# see if an input at the top can filter through to the bottom. At the moment
# flooding does not consider diagonal spaces. 

# TO DO:
#   rename vague variables
#   add comments
#   add functionality for 3D flooding
#   add functionality to compute statistical distributions

import numpy as np
import time


class Porous_grid(object):
    def __init__(self, order=2, edge_len=10, density=0.5):
        self.order = order
        self.edge_len = edge_len
        self.density = density
        self.__build_grid()
        return None

    def __build_grid(self):
        o = self.order
        edge_len = self.edge_len
        self.grid = np.random.uniform(0, 1, edge_len**o)
        a = self.grid > self.density

        # p = [u'\u25A1' if i else u'\u25A0' for i in a]
        p = np.array([' ' if i else u'\u25A0' for i in a])    # Character string
        self.p = p.reshape((edge_len,)*o)

        q = np.array([1 if i else 0 for i in a])
        self.q = q.reshape((edge_len,)*o)           # Numeric matrix
        # print(self.q)
        for i in range(edge_len):
            print(' '.join(self.p[i,:]))
        print('\n')

        self.grid = self.grid.reshape((edge_len,)*o)
        self.p = p
        return None

    def __str__(self):
        return None

    def flood(self):
        # Identify open spaces on top row
        # print(' '.join(self.p[0:self.edge_len]))
        active = []
        b = np.sum(self.q[0,:])
        if b:   # There were values on the first row to flood
            flooding = True
            self.q[0,:] = self.q[0,:] * 2
            for i, val in enumerate(self.q[0,:]):
                if val:
                    active.append((0,i))
        else:
            flooding = False

        while flooding:
            temp = []
            for i in active:
                temp = self.look_around(i, temp)
            active = temp
            self.print_results(self.q, .042)
            
            if not active:
                flooding = False
        return None

    def look_around(self, i, active):
        top_border = self.find_border(i[0], 0)
        left_border = self.find_border(i[1], 0)
        bottom_border = self.find_border(i[0], self.edge_len-1)
        right_border = self.find_border(i[1], self.edge_len-1)

        if not top_border:
            if self.q[i[0]-1, i[1]] == 1:
                self.q[i[0]-1, i[1]] = 2
                active.append((i[0]-1, i[1]))

        if not left_border:
            if self.q[i[0], i[1]-1] == 1:
                self.q[i[0], i[1]-1] = 2
                active.append((i[0], i[1]-1))

        if not bottom_border:
            if self.q[i[0]+1, i[1]] == 1:
                self.q[i[0]+1, i[1]] = 2
                active.append((i[0]+1, i[1]))

        if not right_border:
            if self.q[i[0], i[1]+1] == 1:
                self.q[i[0], i[1]+1] = 2
                active.append((i[0], i[1]+1))
        return active

    def find_border(self, position, wall):
        if position == wall:
            wall = True
        else:
            wall = False
        return wall

    def print_results(self, a, t):
        time.sleep(t)
        b = a.flatten()
        p = np.array([' ' if i==1 else u'\u25A1' if i==2 else u'\u25A0' for i in b])    # Character string

        p = p.reshape((self.edge_len,)*self.order)

        for i in range(self.edge_len):
            print(' '.join(p[i, :]))
        print('\nDensity = {}\n'.format(self.density))
        return


if __name__ == "__main__":
    den = 0.42
    for dense in range(100):
        # den += 0.001
        g = Porous_grid(order=2, edge_len=35, density=den)
        g.flood()
