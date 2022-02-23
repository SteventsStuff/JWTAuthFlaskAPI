import datetime
import typing as t


# not used
class UpdateMixin:

    def update(self, data: t.Dict[str, t.Any]) -> None:
        """Updates model object attributes based on the inout data

        Args:
            data (dict): data to update a current object

        Returns:
            None
        """
        for attr, value in data.items():
            setattr(self, attr, value)


class ExpirationTimeMixin:

    @staticmethod
    def create_exp_timestamp(issued_at: datetime.datetime, token_exp_timeout: int) -> datetime.datetime:
        """Creates a new datetime object based on the "issued_at" datetime with an offset.

        Args:
            issued_at (datetime): datetime when a token was issued
            token_exp_timeout (int): an end time offset

        Returns:
            datetime: datetime object with an offset
        """
        return issued_at + datetime.timedelta(seconds=token_exp_timeout)
