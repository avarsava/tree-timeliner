import argparse
import subprocess
from subprocess import CalledProcessError
import time
import json

TIME_FORMAT = "%b %d %Y %H:%M"
def analyse_time(file, min_time, max_time):
    current_time = parse_in_time(file["time"])
    if current_time < min_time:
        min_time = current_time
    if current_time > max_time:
        max_time = current_time

    if file["type"] == "directory":
        for nested_file in file["contents"]:
            min_time, max_time = analyse_time(nested_file, min_time, max_time)

    return min_time, max_time

def parse_in_time(time_value):
    return time.strptime(time_value, TIME_FORMAT)

def parse_out_time(time_struct):
    return time.strftime(TIME_FORMAT, time_struct)

def main():
    parser = argparse.ArgumentParser(
        prog="tree-timeliner",
        description="Turns a directory tree into a timeline of file modification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('dir',
                        action='store',
                        help='Directory for which to create a tree')
    args = parser.parse_args()

    # Step 1: get the tree
    try:
        # From manpage:
        # -f     Prints the full path prefix for each file.
        # --noreport Omits printing of the file and directory report at the end of the tree listing.
        # -Q     Quote the names of files in double quotes.
        # --timefmt format
        #   Prints (implies -D) and formats the date according to the format string which uses the strftime(3) syntax.
        # -J     Turn on JSON output. Outputs the directory tree as a JSON formatted array.

        result = subprocess.check_output("tree -f --noreport -Q --timefmt '{1}' -J {0}".format(args.dir, TIME_FORMAT),
                                         shell=True, executable="/bin/bash")

    except CalledProcessError:
        for line in result.splitlines():
            print(line.decode())
        exit(1)

    finally:
        json_result = json.loads(result)

    # Step 2: Find the min and max timestamp
    min_time = parse_in_time("Dec 31 2525 23:59")
    max_time = parse_in_time("Jan 1 1900 00:00")
    min_time, max_time = analyse_time(json_result[0], min_time, max_time)

    print("Earliest file at: {0}\nLast file at: {1}".format(parse_out_time(min_time), parse_out_time(max_time)))


if __name__ == "__main__":
    main()