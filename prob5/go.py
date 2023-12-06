import logging
import re
import os
from enum import Enum
from helpers import range_intersect

_logger = logging.getLogger(__name__)

class MapType(Enum):
    SEED_TO_SOIL = 0
    SOIL_TO_FERTILIZER = 1
    FERTILIZER_TO_WATER = 2
    WATER_TO_LIGHT = 3
    LIGHT_TO_TEMPERATURE = 4
    TEMPERATURE_TO_HUMIDITY = 5
    HUMIDITY_TO_LOCATION = 6

MAP_LIST = [
    (MapType.SEED_TO_SOIL, 'seed-to-soil'),
    (MapType.SOIL_TO_FERTILIZER, 'soil-to-fertilizer'),
    (MapType.FERTILIZER_TO_WATER, 'fertilizer-to-water'),
    (MapType.WATER_TO_LIGHT, 'water-to-light'),
    (MapType.LIGHT_TO_TEMPERATURE, 'light-to-temperature'),
    (MapType.TEMPERATURE_TO_HUMIDITY, 'temperature-to-humidity'),
    (MapType.HUMIDITY_TO_LOCATION, 'humidity-to-location'),
]

class MapInfo:
    def __init__(self, dest_start, src_start, len):
        self.src = range(src_start, src_start+len)
        self.dest = range(dest_start, dest_start+len)

    def __repr__(self):
        return f"src: {self.src} -> dest: {self.dest}"

class Almanac:
    def __init__(self):
        self.seeds = []
        self.max_seed = 0
        self.maps = {
            MapType.SEED_TO_SOIL: [],
            MapType.SOIL_TO_FERTILIZER: [],
            MapType.FERTILIZER_TO_WATER: [],
            MapType.WATER_TO_LIGHT: [],
            MapType.LIGHT_TO_TEMPERATURE: [],
            MapType.TEMPERATURE_TO_HUMIDITY: [],
            MapType.HUMIDITY_TO_LOCATION: [],
        }

    def add_seeds(self, seeds):
        i = 0
        while i < len(seeds):
            start = seeds[i]
            stop = start + seeds[i+1]
            self.seeds.append(range(start, stop))
            i += 2
            self.max_seed = max(self.max_seed, stop)

    def update_map(self, type, map_info):
        self.maps[type].append(map_info)

    def _map_src_to_dest(self, type, src):
        map_list = self.maps[type]
        for map in map_list:
            if src >= map.src.start:
                if src < map.src.stop:
                    offset = src - map.src.start
                    return map.dest.start + offset
        return src

    def get_location_for_seed(self, seed):
        src = seed
        for (type,_) in MAP_LIST:
            dest = self._map_src_to_dest(type, src)
            src = dest
        _logger.debug(f"seed {seed} --> location {dest}")
        return dest

    def get_lowest_location_brute(self):
        lowest_location = -1
        for seed_range in self.seeds:
            for seed in seed_range:
                location = self.get_location_for_seed(seed)
                lowest_location = min(location, lowest_location) if lowest_location > 0 else location
        return lowest_location

    def _map_dest_to_src(self, type, dest):
        map_list = self.maps[type]
        for map in map_list:
            if dest >= map.dest.start:
                if dest < map.dest.stop:
                    offset = dest - map.dest.start
                    return map.src.start + offset
        return dest

    def get_seed_for_location(self, location):
        dest = location
        for (type,_) in reversed(MAP_LIST):
            src = self._map_dest_to_src(type, dest)
            dest = src
        _logger.debug(f"location {location} --> seed {src}")
        return src

    def is_seed_valid(self, seed):
        for seed_range in self.seeds:
            if seed in seed_range:
                return True
        return False

    def get_lowest_location_brute2(self):
        location = 0
        while True:
            seed = self.get_seed_for_location(location)
            if self.is_seed_valid(seed):
                return location
            location += 1
            if location % 10000 == 0:
                _logger.info(location)

    def expand_ranges(self, dests):
        current_start = 0
        for dest_range in dests:
            if current_start < dest_range.dest.start:
                yield MapInfo(current_start, current_start, dest_range.dest.start - current_start)
            yield dest_range
            current_start = dest_range.dest.stop

        if current_start < self.max_seed:
            yield MapInfo(current_start, current_start, self.max_seed - current_start)

    def get_srcs_for_dests(self, type, dests):
        maps = list(self.expand_ranges(sorted(self.maps[type], key=lambda map: map.dest.stop)))
        _logger.debug(f"{type} {maps}")
        for dest_range in dests:
            for map in maps:
                dest_intersect = range_intersect(map.dest, dest_range)
                if dest_intersect:
                    offset = dest_intersect.start - map.dest.start
                    length = dest_intersect.stop - dest_intersect.start
                    src_intersect = range(map.src.start + offset, map.src.start + offset + length)
                    yield src_intersect

    def get_lowest_location_fast(self):
        location_maps = sorted(self.maps[MapType.HUMIDITY_TO_LOCATION], key=lambda map: map.dest.stop)
        max_location = location_maps[-1].dest.stop

        location_range = range(0, max_location)
        _logger.debug(f"location range: {location_range}")

        humidity_ranges = list(self.get_srcs_for_dests(MapType.HUMIDITY_TO_LOCATION, [location_range]))
        _logger.debug(f"humidity ranges: {humidity_ranges}")

        temp_ranges = list(self.get_srcs_for_dests(MapType.TEMPERATURE_TO_HUMIDITY, humidity_ranges))
        _logger.debug(f"temp ranges: {temp_ranges}")

        light_ranges = list(self.get_srcs_for_dests(MapType.LIGHT_TO_TEMPERATURE, temp_ranges))
        _logger.debug(f"light ranges: {light_ranges}")

        water_ranges = list(self.get_srcs_for_dests(MapType.WATER_TO_LIGHT, light_ranges))
        _logger.debug(f"water ranges: {water_ranges}")

        fertilizer_ranges = list(self.get_srcs_for_dests(MapType.FERTILIZER_TO_WATER, water_ranges))
        _logger.debug(f"fertilizer ranges: {fertilizer_ranges}")

        soil_ranges = list(self.get_srcs_for_dests(MapType.SOIL_TO_FERTILIZER, fertilizer_ranges))
        _logger.debug(f"soil ranges: {soil_ranges}")

        seed_ranges = list(self.get_srcs_for_dests(MapType.SEED_TO_SOIL, soil_ranges))
        _logger.debug(f"seed ranges: {seed_ranges}")

        for possible_seed_range in seed_ranges:
            _logger.debug(f"seed {possible_seed_range.start} --> location {self.get_location_for_seed(possible_seed_range.start)}")

        for possible_seed_range in seed_ranges:
            for seed_range in self.seeds:
                seed_intersect = range_intersect(possible_seed_range, seed_range)
                if seed_intersect:
                    lowest_location_seed = seed_intersect.start
                    lowest_location = self.get_location_for_seed(seed_intersect.start)
                    _logger.debug(f"found lowest seed: {lowest_location_seed} --> location {lowest_location}")
                    return lowest_location

    def __repr__(self):
        result = f"seeds: {self.seeds}\n"
        for type, map in self.maps.items():
            result += (f"{type} map:\n")
            result += (f"{str(map)}\n")
        return result


def get_almanac(input):
    almanac = Almanac()

    with open(input) as f:
        lines = list(f)
        line_idx = 0

        # seeds: 79 14 55 13
        seeds_match = re.match(r'seeds: ([\d ]+)', lines[line_idx])
        if not seeds_match:
            raise RuntimeError(f"failed to parse line {line_idx}: {lines[line_idx]}")
        line_idx += 1
        almanac.add_seeds([int(seed) for seed in seeds_match.group(1).split()])

        # blank line
        line_idx += 1
        for (type, label) in MAP_LIST:
            # seed-to-soil map:
            map_label_match = re.match(fr'{label} map:', lines[line_idx])
            if not map_label_match:
                raise RuntimeError(f"failed to parse line {line_idx}: {lines[line_idx]}")
            line_idx += 1

            while line_idx < len(lines):
                # 50 98 2
                map_match = re.match(r'(\d+) (\d+) (\d+)', lines[line_idx])
                line_idx += 1
                # got a blank line
                if not map_match:
                    break

                map_info = MapInfo(
                    int(map_match.group(1)),
                    int(map_match.group(2)),
                    int(map_match.group(3)),
                )
                almanac.update_map(type, map_info)

    _logger.debug(f"Almanac: {str(almanac)}")
    return almanac

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

    almanac = get_almanac(args.input)
    # print(f"Minimum seed location (brute): {almanac.get_lowest_location_brute()}")
    # print(f"Minimum seed location (brute2): {almanac.get_lowest_location_brute2()}")
    print(f"Minimum seed location (fast): {almanac.get_lowest_location_fast()}")

if __name__ == "__main__":
    main()