import os
from pathlib import Path

from danfoss_ecl.i18n import detect_lang, normalize_lang, setup_i18n
from danfoss_ecl.paths import dump_dir


def test_normalize_lang():
    assert normalize_lang("da_DK.UTF-8") == "da"
    assert normalize_lang("en-US") == "en"
    assert normalize_lang("sv") == "en"


def test_detect_lang_override(monkeypatch):
    monkeypatch.setenv("ECL310_LANG", "da")
    monkeypatch.setenv("LANG", "en_GB.UTF-8")
    assert detect_lang() == "da"


def test_dump_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("ECL310_OUTPUT_DIR", str(tmp_path / "csv"))
    assert dump_dir() == tmp_path / "csv"


def test_dump_dir_default(monkeypatch):
    monkeypatch.delenv("ECL310_OUTPUT_DIR", raising=False)
    monkeypatch.delenv("ECL310_DUMP_DIR", raising=False)
    path = dump_dir()
    assert path.name == "dumps"
    assert "danfoss-ecl" in path.parts


def test_setup_unknown_falls_back_to_en():
    assert setup_i18n("xx") == "en"
