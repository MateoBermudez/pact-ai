import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_FALLBACK_MODEL = "gemini-3.1-flash-lite"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_models: tuple[str, ...]
    shared_secret: str
    max_file_bytes: int
    max_text_file_chars: int
    structure_timeout_seconds: float
    review_timeout_seconds: float
    screening_timeout_seconds: float


def get_settings() -> Settings:
    primary = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    fallback = os.environ.get("GEMINI_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
    models = (primary,) if not fallback or fallback == primary else (primary, fallback)
    return Settings(
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        gemini_models=models,
        shared_secret=os.environ.get("PACT_AI_SHARED_SECRET", ""),
        max_file_bytes=int(os.environ.get("MAX_FILE_BYTES", str(7 * 1024 * 1024))),
        max_text_file_chars=int(os.environ.get("MAX_TEXT_FILE_CHARS", "20000")),
        structure_timeout_seconds=float(os.environ.get("STRUCTURE_TIMEOUT_SECONDS", "40")),
        review_timeout_seconds=float(os.environ.get("REVIEW_TIMEOUT_SECONDS", "25")),
        screening_timeout_seconds=float(os.environ.get("SCREENING_TIMEOUT_SECONDS", "25")),
    )
