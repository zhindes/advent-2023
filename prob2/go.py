import logging
import re

_logger = logging.getLogger(__name__)

class PullInfo:
    def __init__(self):
        self.red = 0
        self.green = 0
        self.blue = 0

    def __repr__(self):
        return f"red: {self.red}, green: {self.green}, blue: {self.blue}"

class GameInfo:
    def __init__(self, id):
        self.id = id
        self.pulls = []

    def add_pull(self, pull_info):
        self.pulls.append(pull_info)

    def __repr__(self):
        return f"Game {self.id}: {'; '.join([str(pull) for pull in self.pulls])}"

def get_game_info(line):
    # Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
    game_match = re.match(r'Game (\d+): (.*)', line)
    if not game_match:
        raise RuntimeError(f"failed to parse {line}")

    game_id = int(game_match.group(1))
    raw_pulls = game_match.group(2).split('; ')

    game_info = GameInfo(game_id)
    for raw_pull in raw_pulls:
        pull_info = PullInfo()
        for raw_color_str in raw_pull.split(', '):
            color_match = re.match(r'(\d+) (red|green|blue)', raw_color_str)
            if not color_match:
                raise RuntimeError(f"failed to parse {raw_color_str}")
            color_count = int(color_match.group(1))
            color_str = color_match.group(2)
            if color_str == "red":
                pull_info.red = color_count
            elif color_str == "green":
                pull_info.green = color_count
            elif color_str == "blue":
                pull_info.blue = color_count

        game_info.add_pull(pull_info)

    _logger.debug(str(game_info))
    return game_info

def is_game_possible(game_info, max_red, max_green, max_blue):
    possible = True
    for pull in game_info.pulls:
        possible = pull.red <= max_red and pull.blue <= max_blue and pull.green <= max_green
        if not possible:
            break
    _logger.debug(f"game {game_info.id} possible: {possible}")
    return possible

def get_possible_games(all_game_infos, max_red, max_green, max_blue):
    _logger.info(f"getting possible games for max red: {max_red}, max green: {max_green}, max blue: {max_blue}")
    possible_games = []
    for game_info in all_game_infos:
        if is_game_possible(game_info, max_red, max_green, max_blue):
            possible_games.append(game_info.id)
    return possible_games

def get_game_power(game_info):
    fewest_cubes = PullInfo()
    for pull in game_info.pulls:
        fewest_cubes.red = max(fewest_cubes.red, pull.red)
        fewest_cubes.green = max(fewest_cubes.green, pull.green)
        fewest_cubes.blue = max(fewest_cubes.blue, pull.blue)
    _logger.debug(f"game {game_info.id} fewest cubes: {fewest_cubes}")
    return fewest_cubes.red * fewest_cubes.green * fewest_cubes.blue

def get_game_powers(all_game_infos):
    _logger.info(f"getting game powers")
    return [get_game_power(game_info) for game_info in all_game_infos]

def get_all_game_infos(input):
    all_game_infos = []
    with open(input) as f:
        for line in list(f):
            all_game_infos.append(get_game_info(line.strip()))
    return all_game_infos

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--max-red', default=12)
    parser.add_argument('--max-green', default=13)
    parser.add_argument('--max-blue', default=14)
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

    all_game_infos = get_all_game_infos(args.input)
    possible_games = get_possible_games(all_game_infos, args.max_red, args.max_green, args.max_blue)
    print(f"Sum of Possible Game IDs: {sum(possible_games)}")

    game_powers = get_game_powers(all_game_infos)
    print(f"Sum of Game Powers: {sum(game_powers)}")


if __name__ == "__main__":
    main()