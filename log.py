import logging
import typing as t

from flask_log_request_id import RequestIDLogFilter

logger_configs = {
    'level': logging.INFO,
    'filename': 'logs/test.log',
}


class APILogger(logging.Logger):
    _MSG_FORMAT: str = '%(levelname)s: [%(asctime)s] %(name)s :requestId: %(request_id)s :MSG: %(message)s'
    _logger_configs: t.Dict[str, t.Any] = {}

    def __init__(self, name: str) -> None:
        """A logger wrapper class that already have a stream_handler and a file handler configured

        Notes:
            This logger supports a reqeust ID logging

        Args:
            name (str): Logger name
        """

        super().__init__(name)

        # stream_handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(self._MSG_FORMAT))
        stream_handler.addFilter(RequestIDLogFilter())  # << Add request id contextual filter
        self.addHandler(stream_handler)

        # file handler
        file_handler = logging.FileHandler(self._logger_configs.get('filename', 'example.log'))
        file_handler.setFormatter(logging.Formatter(self._MSG_FORMAT))
        file_handler.addFilter(RequestIDLogFilter())
        self.addHandler(file_handler)

        # set level
        self.setLevel(self._logger_configs.get('level', logging.INFO))

    @classmethod
    def configure_logging(cls, configs: t.Dict[str, t.Any]) -> None:
        """Updates a logger configs

        Args:
            configs (dict[str, any]): logger configuration

        Returns:
            None
        """

        cls._logger_configs = configs


APILogger.configure_logging(logger_configs)
