class BDProjectError(Exception):
    pass


class MissingDBUrlError(BDProjectError):
    DEFAULT_MESSAGE = (
        "You must provide a database url in .env (DB_URL) or as an argument (--url)."
    )

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = self.DEFAULT_MESSAGE
        super().__init__(message)
