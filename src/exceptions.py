class APIError(Exception):
    pass


class AppIsNotConfigured(APIError):
    pass


class TokenGeneratorError(APIError):
    pass


class AccessTokenGeneratorError(TokenGeneratorError):
    pass


class ResetPasswordTokenGeneratorError(TokenGeneratorError):
    pass


class TokenDecodeError(APIError):
    pass


class ResetPasswordTokenDecodeError(TokenDecodeError):
    pass


class DBError(APIError):
    pass
