import logging

from logging import Formatter

# Monopoly Game logger
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))

logger = logging.getLogger("com.sbu.monopoly")
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)