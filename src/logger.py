import logging

logging.basicConfig(level=logging.INFO)


class Logger(logging.LoggerAdapter):
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra)


loggerObj = Logger(logger=logging.getLogger(__name__))
