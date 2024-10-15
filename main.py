import argparse
import subprocess
from subprocess import CalledProcessError


def main():
    parser = argparse.ArgumentParser(
        prog="tree-timeliner",
        description="Turns a directory tree into a timeline of file modification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('dir',
                        action='store',
                        help='Directory for which to create a tree')
    args = parser.parse_args()

    try:
        result = subprocess.check_output("tree -a -f --noreport -Q -D {0}".format(args.dir), shell=True, executable="/bin/bash")

    except CalledProcessError as cpe:
        result = cpe.output

    finally:
        for line in result.splitlines():
            print(line.decode())

if __name__ == "__main__":
    main()
