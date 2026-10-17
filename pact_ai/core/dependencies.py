from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from pact_ai.core.cache import TTLCache
from pact_ai.core.config import Settings, get_settings
from pact_ai.core.security import require_internal_token
from pact_ai.llm.base import LLM
from pact_ai.llm.gemini import GeminiLLM


@lru_cache
def get_llm() -> LLM:
    return GeminiLLM(get_settings())


@lru_cache
def get_cache() -> TTLCache:
    return TTLCache(get_settings().cache_ttl_seconds)


SettingsDep = Annotated[Settings, Depends(get_settings)]
LLMDep = Annotated[LLM, Depends(get_llm)]
CacheDep = Annotated[TTLCache, Depends(get_cache)]
Protected = Depends(require_internal_token)
