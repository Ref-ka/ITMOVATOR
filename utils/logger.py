import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir="logs", log_file="api.log", log_level="INFO", console_logging=True):
    """
    Sets up a logger with file and optional console handlers.

    Args:
        log_dir (str): Directory where log files will be stored.
        log_file (str): Name of the log file.
        log_level (str): Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
        console_logging (bool): Whether to enable console logging.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure the logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Full path to the log file
    log_path = os.path.join(log_dir, log_file)

    # Create logger instance
    logger = logging.getLogger("api_logger")

    # Avoid adding duplicate handlers if the logger is already configured
    if logger.hasHandlers():
        return logger

    # Set log level (default to INFO if invalid level is provided)
    log_level = log_level.upper()
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_log_levels:
        log_level = "INFO"
    logger.setLevel(getattr(logging, log_level))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create rotating file handler (max size: 5MB, backups: 3)
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional: Create stream handler (console logs)
    if console_logging:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


# Initialize the logger with dynamic log level and optional console logging
logger = setup_logger(
    log_dir="logs",
    log_file="api.log",
    log_level=os.getenv("LOG_LEVEL", "INFO"),  # Default to INFO if LOG_LEVEL is not set
    console_logging=True  # Set to False in production if console logs are not needed
)