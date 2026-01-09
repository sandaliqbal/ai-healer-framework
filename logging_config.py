import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | " "%(name)s | %(message)s"


def setup_logging(
    level=logging.INFO, log_to_file: bool = False, filename: str = "app.log"
):
    handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(console_handler)

    if log_to_file:
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,  # IMPORTANT: overrides existing configs
    )
