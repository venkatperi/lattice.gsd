import argparse

from image_viewer import ImageViewer
from lattice_runner import LatticeRunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size",
                        type=int,
                        help="Size of the lattice (size x size)",
                        default=100)

    parser.add_argument("-e", "--evolutions",
                        type=int,
                        help="Number of times the lattice evolves",
                        default=0)

    args = parser.parse_args()

    print(args)
    runner = LatticeRunner(args)
    viewer = ImageViewer(width=args.size,
                         height=args.size,
                         runner=runner)
    print("Hit ESC to abort")
    runner.start()
    viewer.start()
    runner.stop()
    runner.join()


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
