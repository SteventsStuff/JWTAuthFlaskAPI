import logging
from flask_log_request_id import RequestIDLogFilter


class APILogger(logging.Logger):
    _MSG_FORMAT: str = "%(levelname)s: %(name)s [%(asctime)s] " \
                       ":requestId: %(request_id)s :MSG: %(message)s"

    def __init__(self, name: str, msg_format: str = None):
        super().__init__(name)
        format_to_use = msg_format or self._MSG_FORMAT
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format_to_use))
        handler.addFilter(RequestIDLogFilter())  # << Add request id contextual filter
        self.addHandler(handler)
