from functools import lru_cache
from pathlib import Path

SYSTEM_DIR = Path(__file__).parent / "system"


@lru_cache
def load_system_prompt(name: str) -> str:
    return (SYSTEM_DIR / f"{name}.md").read_text(encoding="utf-8").strip()
