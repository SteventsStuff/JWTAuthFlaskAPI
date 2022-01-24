import datetime


# not used
class UpdateMixin:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class ExpirationTimeMixin:
    @staticmethod
    def create_exp_timestamp(issued_at: datetime.datetime, token_exp_timeout: int) -> datetime:
        return issued_at + datetime.timedelta(seconds=token_exp_timeout)
