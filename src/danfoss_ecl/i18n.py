"""gettext-style translations from .po files shipped with the package.

Source strings in code are English. Add a language by copying
locale/da/LC_MESSAGES/danfoss_ecl.po to locale/<lang>/LC_MESSAGES/.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

SUPPORTED = ("en", "da")
_DOMAIN = "danfoss_ecl"
_catalog: dict[str, str] = {}
_lang = "en"

_MSG_RE = re.compile(
    r'msgid\s+"(?P<id>(?:\\.|[^"\\])*)"\s+msgstr\s+"(?P<str>(?:\\.|[^"\\])*)"',
    re.MULTILINE,
)


def locale_dir() -> Path:
    return Path(__file__).resolve().parent / "locale"


def parse_po(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    catalog: dict[str, str] = {}
    for match in _MSG_RE.finditer(text):
        msgid = _unescape(match.group("id"))
        msgstr = _unescape(match.group("str"))
        if msgid and msgstr:
            catalog[msgid] = msgstr
    return catalog


def _unescape(value: str) -> str:
    return (
        value.replace(r"\\", "\\")
        .replace(r"\"", '"')
        .replace(r"\n", "\n")
        .replace(r"\t", "\t")
    )


def normalize_lang(value: str | None) -> str:
    if not value:
        return "en"
    code = value.strip().replace("_", "-").split(".")[0].split("-")[0].lower()
    return code if code in SUPPORTED else "en"


def detect_lang() -> str:
    explicit = os.getenv("ECL310_LANG") or os.getenv("ECL310_LANGUAGE")
    if explicit:
        return normalize_lang(explicit)
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        raw = os.getenv(var)
        if raw and raw not in {"C", "POSIX"}:
            return normalize_lang(raw)
    return "en"


def setup_i18n(lang: str | None = None) -> str:
    global _catalog, _lang
    _lang = normalize_lang(lang) if lang else detect_lang()
    _catalog = {}
    if _lang == "en":
        en_path = locale_dir() / "en" / "LC_MESSAGES" / f"{_DOMAIN}.po"
        if en_path.exists():
            _catalog = parse_po(en_path)
        return _lang
    po_path = locale_dir() / _lang / "LC_MESSAGES" / f"{_DOMAIN}.po"
    if po_path.exists():
        _catalog = parse_po(po_path)
    return _lang


def gettext(message: str) -> str:
    return _catalog.get(message, message)


_ = gettext


def current_lang() -> str:
    return _lang
