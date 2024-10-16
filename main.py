import argparse
import os.path
import subprocess
from subprocess import CalledProcessError
import datetime
import json
import collections

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

def build_map(file, map):
    current_time = parse_in_time(file["time"])
    if current_time in map:
        map[current_time].append(file["name"])
    else:
        map[current_time] = [file["name"]]
    if file["type"] == "directory":
        for nested_file in file["contents"]:
            map = build_map(nested_file, map)

    return map

def parse_in_time(time_value):
    return datetime.datetime.strptime(time_value, TIME_FORMAT)

def parse_out_time(time_struct):
    return time_struct.strftime(TIME_FORMAT)

def verbose_print(str, verbose):
    if verbose:
        print(str)

def main():
    parser = argparse.ArgumentParser(
        prog="tree-timeliner",
        description="Turns a directory tree into a timeline of file modification",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('dir',
                        action='store',
                        help='Directory for which to create a tree')
    parser.add_argument("--verbose",
                        "-v",
                        action='store_const',
                        const=True,
                        default=False)
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
        verbose_print(json_result, args.verbose)

    # Step 2: Build Map of Time to List of files
    map = build_map(json_result[0], {})
    verbose_print(map, args.verbose)

    # Step 3: for every sorted map key, output files then and previous
    dates = sorted(map.keys())
    for i in range(0, len(dates)):
        max_date = dates[i]
        files = []
        for j in range(0, i+1):
            files.append(map[dates[j]])


        with open("{0}_{1}".format(os.path.basename(args.dir), parse_out_time(max_date)), mode="w") as f:
            verbose_print(files, args.verbose)
            f.write(str(files))

if __name__ == "__main__":
    main()