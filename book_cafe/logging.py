import logging
from logging import handlers

from configuration import LOGFILE_NAME, LOGFILES_MAX_BYTES, NUM_OF_LOGFILE_BACKUPS

logger = logging.getLogger(__name__)
handler = handlers.RotatingFileHandler(filename=LOGFILE_NAME, maxBytes=LOGFILES_MAX_BYTES,
                                       backupCount=NUM_OF_LOGFILE_BACKUPS)
formater = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    pass