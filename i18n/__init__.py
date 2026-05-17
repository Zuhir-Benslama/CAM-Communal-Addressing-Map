"""Lightweight i18n helper — loads .ts translation files at runtime."""
import xml.etree.ElementTree as ET
import os


_cache: dict[str, dict[str, str]] = {}


def load_translations(locale: str, ts_dir: str | None = None) -> dict[str, str]:
    """Load translations from RNA_{locale}.ts, returns {source: translation}."""
    if locale in _cache:
        return _cache[locale]

    if ts_dir is None:
        ts_dir = os.path.dirname(__file__)

    ts_path = os.path.join(ts_dir, f"RNA_{locale}.ts")
    if not os.path.exists(ts_path):
        _cache[locale] = {}
        return _cache[locale]

    tree = ET.parse(ts_path)
    root = tree.getroot()
    mapping: dict[str, str] = {}
    for context in root.findall(".//context"):
        for msg in context.findall("message"):
            src = msg.find("source")
            trans = msg.find("translation")
            if src is not None and trans is not None and trans.text:
                mapping[src.text or ""] = trans.text
    _cache[locale] = mapping
    return mapping


def tr(source: str, locale: str = "ar") -> str:
    """Translate source string to the given locale."""
    mapping = load_translations(locale)
    return mapping.get(source, source)
