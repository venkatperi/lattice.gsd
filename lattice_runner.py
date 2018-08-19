import time
from threading import Thread

from lattice import Lattice


class LatticeRunner(Thread):

    def __init__(self, args):
        Thread.__init__(self)
        self.args = args
        self.lattice = Lattice(size=args.size, slider=0,
                               onlyRedBlue=True, numRatio=20,
                               deathRate=100000)
        self.args = args
        self.quit = False

    def stop(self):
        self.quit = True

    def run(self):
        for iteration in range(0, self.args.evolutions):
            self.lattice.evolve(1)
            if self.quit:
                print("Aborting")
                break
        print("Generations: %d" % self.lattice.generation)
