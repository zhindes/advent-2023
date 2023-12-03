import logging
import re
from enum import Enum

_logger = logging.getLogger(__name__)

class ComponentType(Enum):
    EMPTY = 0
    NUMBER = 1
    GEAR = 2
    SYMBOL = 3

class Component:
    def __init__(self, type, value, pos, width):
        self.type = type
        self.value = value
        self.pos = pos
        self.width = width

class Row:
    def __init__(self, raw_line):
        self.raw_line = raw_line
        self.comps = []

        components = re.split(r'(\d+|[!@#$%^&*\\/\+=-])', self.raw_line)
        _logger.debug(components)

        pos = 0
        for comp in components:
            # split returns empty strings match groups that touch
            if not comp:
                continue

            num_match = re.match(r'\d+', comp)
            gear_match = re.match(f'\*', comp)
            symbol_match = re.match(r'[!@#$%^&*\\/\+=-]', comp)
            empty_match = re.match(r'\.+', comp)
            if num_match:
                self.comps.append(Component(ComponentType.NUMBER, int(comp), pos, len(comp)))
            elif gear_match:
                self.comps.append(Component(ComponentType.GEAR, comp, pos, 1))
            elif symbol_match:
                self.comps.append(Component(ComponentType.SYMBOL, comp, pos, 1))
            elif empty_match:
                self.comps.append(Component(ComponentType.EMPTY, comp, pos, len(comp)))
                pass
            else:
                raise RuntimeError(f"unexpected components {comp}")
            pos += len(comp)

    def get_numbers(self):
        return [comp for comp in self.comps if comp.type == ComponentType.NUMBER]

    def get_gears(self):
        return [comp for comp in self.comps if comp.type == ComponentType.GEAR]

    def get_comps_in_block(self, start_x, end_x, types):
        # start and end is inclusive
        comps = []
        for comp in self.comps:
            if comp.type in types:
                comp_start = comp.pos
                comp_end = comp.pos + comp.width - 1

                # ....xxx....
                # .yy........
                component_before = comp_end < start_x
                # ....xxx....
                # ........yy.
                component_after = comp_start > end_x

                # it must intersect!
                if not component_before and not component_after:
                    comps.append(comp)
        return comps

    def __repr__(self):
        repr = ""
        for comp in self.comps:
            if comp.type == ComponentType.EMPTY:
                repr += '.'*comp.width
            else:
                repr += str(comp.value)
        return repr

    def __len__(self):
        last_comp = self.comps[-1]
        return last_comp.pos + last_comp.width

class Schematic:
    def __init__(self):
        self.rows = []
        self.width = -1

    def add_row(self, row):
        if self.width < 0:
            self.width = len(row)
        elif self.width != len(row):
            raise RuntimeError(f"Width of {str(row)} doesn't match existing width, {self.width}")
        self.rows.append(row)

    def _get_comps_adjacent(self, comp, y, types):
        # start and end is inclusive
        start_x = max(0, comp.pos - 1)
        start_y = max(0, y - 1)
        end_x = min(self.width - 1, comp.pos + comp.width)
        end_y = min(len(self.rows) - 1, y + 1)
        _logger.debug(f"looking for {types} in ({start_x}, {start_y}) --> ({end_x}, {end_y})")

        comps = []
        for y in range(start_y, end_y + 1):
            comps.extend(self.rows[y].get_comps_in_block(start_x, end_x, types))
        return comps

    def get_part_numbers(self):
        # part number is any number adjacent to a symbol
        part_numbers = []
        for y, row in enumerate(self.rows):
            for number in row.get_numbers():
                adjacent_comps = self._get_comps_adjacent(number, y, [ComponentType.GEAR, ComponentType.SYMBOL])
                if len(adjacent_comps) > 0:
                    _logger.debug(f"{number.value} is a part number")
                    part_numbers.append(number.value)
                else:
                    _logger.debug(f"{number.value} is NOT a part number")
        return part_numbers

    def get_gear_ratios(self):
        # a gear is any * symbol that is adjacent to exactly two part numbers
        gear_ratios = []
        for y, row in enumerate(self.rows):
            for gear in row.get_gears():
                adjacent_comps = self._get_comps_adjacent(gear, y, [ComponentType.NUMBER])
                if len(adjacent_comps) == 2:
                    _logger.debug(f"({gear.pos}, {y}) is a gear")
                    # ratio is the two number values multiplied
                    gear_ratios.append(adjacent_comps[0].value * adjacent_comps[1].value)
                else:
                    _logger.debug(f"({gear.pos}, {y}) is NOT a gear")
        return gear_ratios

    def __repr__(self):
        return "\n".join([str(row) for row in self.rows])

def get_schematic(input):
    schematic = Schematic()
    with open(input) as f:
        for line in list(f):
            schematic.add_row(Row(line.strip()))

    _logger.debug(str(schematic))
    return schematic

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

    schematic = get_schematic(args.input)
    part_numbers = schematic.get_part_numbers()
    print(f"Sum of Part Numbers: {sum(part_numbers)}")
    gear_ratios = schematic.get_gear_ratios()
    print(f"Sum of Gear Ratios: {sum(gear_ratios)}")


if __name__ == "__main__":
    main()