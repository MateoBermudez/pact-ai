import pytest
from fastapi.testclient import TestClient

from pact_ai.core.cache import TTLCache
from pact_ai.core.config import get_settings
from pact_ai.core.dependencies import get_cache, get_llm
from pact_ai.main import app
from tests.helpers import FakeLLM


@pytest.fixture
def llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def client(llm: FakeLLM):
    app.dependency_overrides[get_llm] = lambda: llm
    app.dependency_overrides[get_cache] = lambda: TTLCache(0)
    get_settings.cache_clear()
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()
