import logging

_logger = logging.getLogger(__name__)

def sum_cal_values(cal_doc):
    _logger.info("summing cal values")
    _logger.debug("a debug trace")
    return 0

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

    sum = sum_cal_values(args.cal_doc)
    print(f"Sum of Calibration Values: {sum}")

if __name__ == "__main__":
    main()