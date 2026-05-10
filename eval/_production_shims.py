"""Compatibility shims for production's `src.*` self-imports.

Why this exists
---------------
The production repo imports its own modules using a `src.` prefix
(`from src.bok_compensation_typedb.llm import ...`). For the prefix to
resolve, the production root must be on sys.path so `src/` is picked up as
an implicit namespace package.

Additionally, `llm.py` was renamed to `llm_template.py` but the importing
sites were not updated, so `from src.bok_compensation_typedb.llm import X`
still fails after path setup. We register a module alias to bridge the
old name.

Per CLAUDE.md the production repo must not be modified, so all fixes live
here in eval/.

Call `install()` before importing any production module.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

DEFAULT_PRODUCTION_ROOT = Path("/Users/user/vibe/bok-compensation-regulations")


def install(production_root: str | os.PathLike | None = None) -> Path:
    root = Path(production_root or os.environ.get("BOK_PRODUCTION_ROOT")
                or DEFAULT_PRODUCTION_ROOT)
    if not root.exists():
        raise RuntimeError(
            f"BOK production root not found: {root}. "
            f"Set BOK_PRODUCTION_ROOT env var or pass production_root explicitly."
        )

    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    try:
        llm_template = importlib.import_module("bok_compensation_typedb.llm_template")
    except ImportError as e:
        raise RuntimeError(
            f"Cannot import bok_compensation_typedb.llm_template — "
            f"is the production package installed?  "
            f"Run `pip install -e \"{root}[llm]\"` first.  ({e})"
        ) from e

    # Old name `llm` still referenced by context_query / agent.py — alias it.
    sys.modules.setdefault("src.bok_compensation_typedb.llm", llm_template)
    sys.modules.setdefault("bok_compensation_typedb.llm", llm_template)
    return root
