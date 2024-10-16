import argparse
import subprocess
from subprocess import CalledProcessError
import datetime
import json
import os.path

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
    return datetime.datetime.strptime(time_value, TIME_FORMAT)

def parse_out_time(time_struct):
    return time_struct.strftime(TIME_FORMAT)

def increment_time(time_struct):
    return time_struct + datetime.timedelta(minutes=1)

def slice_json(file, slice_time):
    sliced_json=[]
    if parse_in_time(file["time"]) <= slice_time:
        sliced_json.append(file)
    if file["type"] == "directory":
        for nested_file in file["contents"]:
            more_sliced_json = slice_json(nested_file, slice_time)
            if more_sliced_json: # Avoid appending []
                sliced_json.append(more_sliced_json)
    return sliced_json

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

    # Step 2: Find the min and max timestamp
    min_time = parse_in_time("Dec 31 2525 23:59")
    max_time = parse_in_time("Jan 1 1900 00:00")
    min_time, max_time = analyse_time(json_result[0], min_time, max_time)

    verbose_print("Earliest file at: {0}\nLast file at: {1}"
                  .format(parse_out_time(min_time), parse_out_time(max_time)),
                  args.verbose)

    # Step 3: Take snapshots between min and max time
    slice_time = min_time
    old_json = slice_json(json_result[0], slice_time)
    verbose_print("{0}: {1}".format(slice_time, old_json), args.verbose)
    while slice_time <= max_time:
        slice_time = increment_time(slice_time)
        new_json = slice_json(json_result[0], slice_time)
        if len(old_json) < len(new_json):
            old_json = new_json
            verbose_print("{0}: {1}".format(slice_time, old_json), args.verbose)
            with open("{0}_{1}.json".format(os.path.basename(args.dir), parse_out_time(slice_time)), mode='w') as f:
                f.write(str(old_json))

if __name__ == "__main__":
    main()