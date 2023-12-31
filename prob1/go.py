import logging
import re

_logger = logging.getLogger(__name__)

def get_first_digit(line):
    digit_match = re.search(r'(\d)', line)
    if not digit_match:
        raise RuntimeError(f"failed to find a digit in {line}")
    digit_str = digit_match.group(1)
    digit = int(digit_str)
    _logger.debug(f"digit: {digit_str}: {digit}")
    return digit


def get_cal_value_naive(line):
    # On each line, the calibration value can be found by combining the first
    # digit and the last digit (in that order) to form a single two-digit
    # number.
    _logger.info(f"getting cal value for {line}")
    first_digit = get_first_digit(line)
    reversed_line = line[::-1]
    last_digit = get_first_digit(reversed_line)

    cal_value = first_digit * 10 + last_digit
    _logger.info(f"cal value for {line}: {cal_value}")
    return cal_value


NUMBERS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine"
]


def get_all_digits(line):
    all_digits = []
    for start_index in range(len(line)):
        if line[start_index].isdigit():
            all_digits.append(int(line[start_index]))
        else:
            for num_index, num_str in enumerate(NUMBERS):
                sub_line = line[start_index:start_index+len(num_str)]
                if sub_line == num_str:
                    all_digits.append(num_index+1)
                    # we can't skip ahead since "oneight" is valid

    _logger.debug(f"all digits: {line}: {all_digits}")
    return all_digits


def get_cal_value(line):
    # On each line, the calibration value can be found by combining the first
    # digit and the last digit (in that order) to form a single two-digit
    # number.
    # It looks like some of the digits are actually spelled out with letters.
    all_digits = get_all_digits(line)
    first_digit = all_digits[0]
    last_digit = all_digits[-1]
    cal_value = first_digit * 10 + last_digit
    _logger.info(f"cal value for {line}: {cal_value}")
    return cal_value


def get_cal_values(cal_doc):
    _logger.info("summing cal values")
    with open(cal_doc) as f:
        cal_values = [get_cal_value(line.strip()) for line in list(f)]
    return cal_values

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--cal-doc', required=True)
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()

    verbosity = 2 - args.verbose
    logging_level = {
        0: logging.DEBUG,
        1: logging.INFO,
        2: logging.WARNING,
        3: logging.ERROR,
        4: logging.CRITICAL,
    }[verbosity]
    log_format = "[%(relativeCreated)6d] %(levelname)-5s %(funcName)s: %(message)s"
    logging.basicConfig(level=logging_level, format=log_format)

    sum_val_values = sum(get_cal_values(args.cal_doc))
    print(f"Sum of Calibration Values: {sum_val_values}")

if __name__ == "__main__":
    main()