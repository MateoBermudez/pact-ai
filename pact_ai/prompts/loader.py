from functools import lru_cache
from pathlib import Path

SYSTEM_DIR = Path(__file__).parent / "system"


@lru_cache
def load_system_prompt(name: str, **values: str) -> str:
    text = (SYSTEM_DIR / f"{name}.md").read_text(encoding="utf-8").strip()
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text
