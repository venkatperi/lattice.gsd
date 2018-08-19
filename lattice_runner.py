import time
from threading import Thread

from lattice import Lattice


class LatticeRunner(Thread):

    def __init__(self, args):
        Thread.__init__(self)
        self.args = args
        self.lattice = Lattice(size=args.size,
                               slider=args.slider,
                               onlyRedBlue=not args.any,
                               defKillers=args.defKillers,
                               density=args.density,
                               numRatio=args.numRatio,
                               redAdvantage=args.redAdvantage,
                               blueAdvantage=args.blueAdvantage,
                               redGrowth=args.redGrowth,
                               blueGrowth=args.blueGrowth,
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
