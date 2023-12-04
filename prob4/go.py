import logging
import re
from enum import Enum

_logger = logging.getLogger(__name__)

class Scratcher:
    def __init__(self, card_number):
        self.card_number = card_number
        self.winning_numbers = set()
        self.my_numbers = set()

    def __repr__(self):
        return f"Card {self.card_number}: {self.winning_numbers} | {self.my_numbers}"

    def num_matches(self):
        intersection = self.winning_numbers & self.my_numbers
        return len(intersection)

    def get_points(self):
        num_matches = self.num_matches()
        if num_matches == 0:
            points = 0
        else:
            points = 2 ** (num_matches - 1)
        _logger.debug(f"Card {self.card_number}: {num_matches} matches: {points} points")
        return points

def get_scratcher(line):
    scratch_match = re.match(r'Card\s+(\d+): ([\d ]+) \| ([\d ]+)', line)
    if not scratch_match:
        raise RuntimeError(f"failed to parse scratcher: {line}")

    scratcher = Scratcher(int(scratch_match.group(1)))
    for winning_number_raw in scratch_match.group(2).split():
        scratcher.winning_numbers.add(int(winning_number_raw))

    for my_number_raw in scratch_match.group(3).split():
        scratcher.my_numbers.add(int(my_number_raw))

    _logger.debug(str(scratcher))
    return scratcher


def get_scratchers(input):
    scratchers = []
    with open(input) as f:
        return [get_scratcher(line.strip()) for line in list(f)]
    return schematic

def play_scratchers(scratchers):
    # if we're looking at Card X and N is the number of matching numbers
    # then we get to play copies of Card X+1, ..., Card X+N

    # list of cards we get to play, originally all the "physical" copies
    total_scratcher_count = len(scratchers)
    scratcher_stack = list(range(total_scratcher_count))

    played_scratcher_count = 0
    while scratcher_stack:
        played_scratcher_count += 1
        current_idx = scratcher_stack.pop()
        current = scratchers[current_idx]

        num_matches = current.num_matches()
        free_start_idx = current_idx + 1
        free_stop_idx = free_start_idx + num_matches
        free_idxs = [free_idx for free_idx in range(free_start_idx, free_stop_idx) if free_idx < total_scratcher_count]
        scratcher_stack.extend(free_idxs)

    return played_scratcher_count


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
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

    scratchers = get_scratchers(args.input)
    scratcher_points = [scratcher.get_points() for scratcher in scratchers]
    print(f"Sum of Points: {sum(scratcher_points)}")
    print(f"Total Scratchcards Played: {play_scratchers(scratchers)}")


if __name__ == "__main__":
    main()