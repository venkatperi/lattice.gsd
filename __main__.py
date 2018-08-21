import argparse
import pprint

from image_viewer import ImageViewer
from lattice_runner import LatticeRunner


def zero_to_one(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]" % (x,))
    return x


def main():
    args = parse_args()
    pprint.pprint(vars(args))

    runner = LatticeRunner(args)
    viewer = ImageViewer(width=args.size,
                         height=args.size,
                         updateRate=args.updateRate,
                         runner=runner)
    print("Hit ESC to abort")
    runner.start()
    viewer.start()
    runner.stop()
    runner.join()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size",
                        type=int,
                        help="Size of the lattice (size x size)",
                        default=50)
    parser.add_argument("-e", "--evolutions",
                        type=int,
                        help="Number of generations the lattice evolves",
                        default=1000000)
    parser.add_argument("--slider",
                        type=zero_to_one,
                        help="If slider is 0 then only killing happens, if slider is 1 then only "
                             "'random death' and for a range between it's a mixture. Default 0.",
                        default=0)
    parser.add_argument("--any",
                        action="store_true",
                        help="If set, the lattice contains any, otherwise only red and blue "
                             "bacteria")
    parser.add_argument("--redAdvantage",
                        type=float,
                        help="Red Killing disparity, 1 means equal killers.",
                        default=1)
    parser.add_argument("--blueAdvantage",
                        type=float,
                        help="Blue Killing disparity, 1 means equal killers.",
                        default=1)
    parser.add_argument("--redGrowth",
                        type=float,
                        help="1 for equal growth",
                        default=1)
    parser.add_argument("--blueGrowth",
                        type=float,
                        help="1 for equal growth",
                        default=1)
    parser.add_argument("--defKillers",
                        action="store_true",
                        help="if set (defective killers), killers then red and blue can't kill "
                             "each other.")
    parser.add_argument("--density",
                        type=zero_to_one,
                        help="overall cell density at initialization of the lattice.",
                        default=1)
    parser.add_argument("--numRatio",
                        type=zero_to_one,
                        help="overall number ratio (number of blue/ total number of cells)",
                        default=1)
    parser.add_argument("--updateRate",
                        type=int,
                        help="Rate at which display is updated (Hz)",
                        default=60)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
