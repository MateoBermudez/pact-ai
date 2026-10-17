class LLMUnavailable(Exception):
    pass


class FileRejected(Exception):
    def __init__(self, filename: str, reason: str, status_code: int = 415) -> None:
        super().__init__(f"{filename}: {reason}")
        self.filename = filename
        self.reason = reason
        self.status_code = status_code
