import logging
import sys

class MetaLogger(type):
    """Metaclass that adds logging capability to any class"""
    logger: logging.Logger

    def __new__(cls, name, bases, attrs):
        logger = logging.getLogger(name)
        attrs['logger'] = logger

        # Get default log level from class attribute, or use INFO
        default_level = attrs.get('_default_log_level', logging.INFO)

        def log(self, message, level=None):
            actual_level = level or getattr(self, '_default_log_level', default_level)
            self.logger.log(actual_level, message)

        attrs['log'] = log
        return super().__new__(cls, name, bases, attrs)

# Configure logging
def setup_logging(debug: bool = True):
    """Configure application logging"""
    log_level = logging.DEBUG if debug else logging.INFO

    # Custom formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Root logger configuration
    logging.root.setLevel(log_level)
    logging.root.addHandler(console_handler)

    # Reduce noise from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)