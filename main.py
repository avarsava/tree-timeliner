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
        # From manpage:
        # -a     All files are printed.  By default tree does not print hidden files (those beginning with a dot `.').
        #   In no event does tree print the file system constructs `.' (current directory) and  `..' (previous directory)
        # -f     Prints the full path prefix for each file.
        # --noreport Omits printing of the file and directory report at the end of the tree listing.
        # -Q     Quote the names of files in double quotes.
        # -D     Print the date of the last modification time or if -c is used, the last status change time for the
        #   file listed.

        result = subprocess.check_output("tree -a -f --noreport -Q -D {0}".format(args.dir), shell=True, executable="/bin/bash")

    except CalledProcessError as cpe:
        result = cpe.output

    finally:
        for line in result.splitlines():
            print(line.decode())

if __name__ == "__main__":
    main()
