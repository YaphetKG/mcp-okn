"""Metadata folders shipped with the server.

``metadata/void_entities`` (the per-KG schema files) and ``metadata/descriptions``
(one description per KG) live in the repository's ``metadata`` folder. A built wheel
carries copies under ``mcp_okn/data/`` (the hatch ``force-include`` table in
``pyproject.toml``), while a checkout or an editable install has no such copy and
reads the repository folder directly.
"""

from __future__ import annotations

from importlib import resources
from pathlib import Path

#: ``<repo>/metadata``, seen from ``<repo>/src/mcp_okn/bundled.py``.
_REPO_METADATA = Path(__file__).resolve().parents[2] / "metadata"


def metadata_dir(name: str) -> Path | None:
    """The shipped copy of ``metadata/<name>``, or ``None`` if neither copy exists."""
    packaged = Path(str(resources.files("mcp_okn") / "data" / name))
    for candidate in (packaged, _REPO_METADATA / name):
        if candidate.is_dir():
            return candidate
    return None
