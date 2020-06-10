import itertools
import math
import csv
import os
import argparse


def parse_command_line():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--txt-file", required=True, help="The input txt file to parse."
    )
    parser.add_argument(
        "--wells",
        required=True,
        help="CSV file containing information about the wells.",
    )

    return parser.parse_args()


def read_chunk(f):

    # we discard the first 11 lines
    for _ in range(11):
        _ = next(f)

    # next line contains number of replicate and hours
    # but we don't use this information
    _ = next(f)

    # next 8 lines are 590 nm
    data_590_nm = []
    for _ in range(8):
        line = next(f)
        data_590_nm += list(map(float, line.split()))

    # next 8 lines are 750 nm
    data_750_nm = []
    for _ in range(8):
        line = next(f)
        data_750_nm += list(map(float, line.split()))

    # one empty line at the end
    _ = next(f)

    return data_590_nm, data_750_nm


def zip_to_list_of_tuples(lists):
    """
    For instance when sending in [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    this function will return [(1, 4, 7), (2, 5, 8), (3, 6, 9)].

    The latter is practical for computing averages and standard deviations.
    """
    return list(zip(*lists))


def average(numbers):
    return sum(numbers) / len(numbers)


def std_dev(numbers):
    a = average(numbers)
    n = len(numbers)
    s = 0.0
    for number in numbers:
        s += (number - a) ** 2.0
    return math.sqrt(s / n)


def read_data(file_name):
    with open(file_name, "r") as f:
        data_590_nm = []
        data_750_nm = []

        # this is done this way to allow for more than 3 plates, it could be in
        # fact any number of plates
        try:
            while True:
                data_590_nm_plate, data_750_nm_plate = read_chunk(f)
                data_590_nm.append(data_590_nm_plate)
                data_750_nm.append(data_750_nm_plate)
        except StopIteration:
            pass

        data_590_nm_tuples = zip_to_list_of_tuples(data_590_nm)
        data_750_nm_tuples = zip_to_list_of_tuples(data_750_nm)

        return data_590_nm_tuples, data_750_nm_tuples


def compute_statistics(tuples):
    averages = map(average, tuples)
    std_devs = map(std_dev, tuples)
    return list(averages), list(std_devs)


def read_wells(csv_file):
    labels = []
    sources = []
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels.append(row["Well"])
            sources.append(row["C-Source"])
    return labels, sources


def extract_hours_from_filename(file_name):
    without_suffix = os.path.splitext(file_name)[0]
    after_underscore = without_suffix.split("_")[-1]
    hours = int(after_underscore.replace("h", ""))
    return hours


def print_output(*args):
    for row in zip_to_list_of_tuples([*args]):
        print(",".join(map(str, row)))


if __name__ == "__main__":
    args = parse_command_line()

    data_590_nm_tuples, data_750_nm_tuples = read_data(args.txt_file)

    averages_590_nm, std_devs_590_nm = compute_statistics(data_590_nm_tuples)
    averages_750_nm, std_devs_750_nm = compute_statistics(data_750_nm_tuples)

    lns_590_nm = list(map(math.log, averages_590_nm))
    lns_750_nm = list(map(math.log, averages_750_nm))

    labels, sources = read_wells(args.wells)

    # we need a list of hours of the same length as the other lists (e.g.
    # sources)
    hours = [extract_hours_from_filename(args.txt_file)] * len(sources)

    # we round everything to 3 digits after the comma
    num_digits = 3
    averages_590_nm = list(map(lambda x: round(x, num_digits), averages_590_nm))
    std_devs_590_nm = list(map(lambda x: round(x, num_digits), std_devs_590_nm))
    lns_590_nm = list(map(lambda x: round(x, num_digits), lns_590_nm))
    averages_750_nm = list(map(lambda x: round(x, num_digits), averages_750_nm))
    std_devs_750_nm = list(map(lambda x: round(x, num_digits), std_devs_750_nm))
    lns_750_nm = list(map(lambda x: round(x, num_digits), lns_750_nm))

    print_output(
        labels,
        sources,
        hours,
        averages_750_nm,
        std_devs_750_nm,
        lns_750_nm,
        averages_590_nm,
        std_devs_590_nm,
        lns_590_nm,
    )
