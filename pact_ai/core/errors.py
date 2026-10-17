class PactAiError(Exception):
    status_code = 500

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class FileRejected(PactAiError):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code


class AiNotConfigured(PactAiError):
    status_code = 503


class AiUpstreamError(PactAiError):
    status_code = 502
