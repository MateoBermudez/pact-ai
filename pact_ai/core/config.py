import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    gemini_fallback_model: str
    internal_token: str
    llm_attempt_timeout: float
    llm_total_budget: float
    temperature: float
    max_amount_mon: float
    max_text_chars: int
    max_files: int
    max_file_bytes: int
    max_total_bytes: int
    max_document_chars: int
    cache_ttl_seconds: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        gemini_fallback_model=os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite"),
        internal_token=os.getenv("INTERNAL_API_TOKEN", ""),
        llm_attempt_timeout=float(os.getenv("LLM_ATTEMPT_TIMEOUT_SECONDS", "12")),
        llm_total_budget=float(os.getenv("LLM_TOTAL_BUDGET_SECONDS", "14")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_amount_mon=float(os.getenv("MAX_AMOUNT_MON", "50")),
        max_text_chars=int(os.getenv("MAX_TEXT_CHARS", "8000")),
        max_files=int(os.getenv("MAX_FILES", "3")),
        max_file_bytes=int(os.getenv("MAX_FILE_BYTES", str(8 * 1024 * 1024))),
        max_total_bytes=int(os.getenv("MAX_TOTAL_BYTES", str(15 * 1024 * 1024))),
        max_document_chars=int(os.getenv("MAX_DOCUMENT_CHARS", "30000")),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "600")),
    )
