"""UI widget i18n (from widgets.json / strings.json)."""

import json
import os

_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'template_data',
)

_str_cache: dict[str, dict[str, str]] = {}


def _get_string(source: str, locale: str) -> str:
    """Look up a source string in strings.json for the given locale."""
    if 'strings' not in _str_cache:
        path = os.path.join(_DATA_DIR, 'strings.json')
        with open(path, encoding='utf-8') as f:
            _str_cache['strings'] = json.load(f)
    data = _str_cache['strings'].get(source)
    if isinstance(data, dict):
        return data.get(locale, data.get('ar', source))
    return source


_widgets_data: dict[str, dict[str, str]] | None = None


def _load_widgets() -> dict[str, dict[str, str]]:
    """Load and cache widgets.json data."""
    global _widgets_data  # pylint: disable=global-statement
    if _widgets_data is None:
        path = os.path.join(_DATA_DIR, 'widgets.json')
        with open(path, encoding='utf-8') as f:
            _widgets_data = json.load(f)
    return _widgets_data


def widget_text(object_name: str, locale: str) -> str:
    """Return localized text for a widget by objectName."""
    data = _load_widgets().get(object_name)
    if data:
        return data.get(locale, data.get('ar', ''))
    return ''


def get_string(source: str, locale: str) -> str:
    """Return localized string for a source text from strings.json."""
    return _get_string(source, locale)


def clear_i18n_cache() -> None:
    """Clear the cached strings.json data."""
    _str_cache.pop('strings', None)


def _src_text(w, attr='text'):
    """Get or cache the original Arabic source text on a widget.
    Uses attr-specific cache attribute (_cam_src, _cam_src_tip, _cam_src_win)
    to avoid clashes when a widget appears in multiple findChildren passes."""
    cache_attr = {
        'text': '_cam_src',
        'title': '_cam_src',
        'placeholder': '_cam_src',
        'tooltip': '_cam_src_tip',
        'windowtitle': '_cam_src_win',
    }.get(attr, '_cam_src')
    cached = getattr(w, cache_attr, None)
    if cached is not None:
        return cached
    getters = {
        'text': getattr(w, 'text', lambda: ''),
        'title': getattr(w, 'title', lambda: ''),
        'placeholder': getattr(w, 'placeholderText', lambda: ''),
        'tooltip': getattr(w, 'toolTip', lambda: ''),
        'windowtitle': getattr(w, 'windowTitle', lambda: ''),
    }
    src = getters.get(attr, lambda: '')()
    if src:
        setattr(w, cache_attr, src)
    return src


def _translate_text(src: str, locale: str) -> str:
    """Translate a source string via _get_string, or return empty."""
    if not src:
        return ''
    translated = _get_string(src, locale)
    return translated if translated != src else ''


def _set_from_lookup(
    w, locale, widgets_data, *, attr='text', setter='setText', src_attr=None
) -> None:
    """Set a widget attribute from widgets_data or _src_text fallback."""
    name = w.objectName()
    if name in widgets_data:
        value = widgets_data[name].get(
            locale,
            widgets_data[name].get('ar', ''),
        )
        getattr(w, setter)(value)
        return
    src = _src_text(w, src_attr or attr)
    if src:
        translated = _translate_text(src, locale)
        if translated:
            getattr(w, setter)(translated)


def _translate_labels(dialog, locale, widgets_data) -> None:
    """Translate QLabel, QPushButton, QCheckBox text."""
    from qgis.PyQt.QtWidgets import (  # pylint: disable=import-outside-toplevel
        QCheckBox,
        QLabel,
        QPushButton,
    )

    for w in dialog.findChildren((QLabel, QPushButton, QCheckBox)):
        _set_from_lookup(w, locale, widgets_data)


def _translate_groupbox(dialog, locale, widgets_data) -> None:
    """Translate QGroupBox titles."""
    from qgis.PyQt.QtWidgets import QGroupBox  # pylint: disable=import-outside-toplevel

    for w in dialog.findChildren(QGroupBox):
        _set_from_lookup(w, locale, widgets_data, attr='title', setter='setTitle')


def _translate_placeholder(dialog, locale) -> None:
    """Translate QLineEdit placeholder text."""
    from qgis.PyQt.QtWidgets import QLineEdit  # pylint: disable=import-outside-toplevel

    for w in dialog.findChildren(QLineEdit):
        src = _src_text(w, 'placeholder')
        if src:
            translated = _translate_text(src, locale)
            if translated:
                w.setPlaceholderText(translated)


def _translate_tabs(dialog, locale) -> None:
    """Translate QTabWidget tab texts using cached source strings."""
    from qgis.PyQt.QtWidgets import (
        QTabWidget,  # pylint: disable=import-outside-toplevel
    )

    for w in dialog.findChildren(QTabWidget):
        if not hasattr(w, '_cam_tab_src'):
            w._cam_tab_src = [w.tabText(i) for i in range(w.count())]
        for i in range(w.count()):
            src = w._cam_tab_src[i]
            if src:
                w.setTabText(i, _get_string(src, locale))


def _translate_window_title(dialog, locale) -> None:
    """Translate dialog window title."""
    if not hasattr(dialog, 'windowTitle'):
        return
    src = _src_text(dialog, 'windowtitle')
    if src:
        translated = _translate_text(src, locale)
        if translated:
            dialog.setWindowTitle(translated)


def _translate_tooltips(dialog, locale, widgets_data) -> None:
    """Translate QWidget tooltips."""
    from qgis.PyQt.QtWidgets import QWidget  # pylint: disable=import-outside-toplevel

    for w in dialog.findChildren(QWidget):
        name = w.objectName()
        tip = _src_text(w, 'tooltip')
        if not tip:
            continue
        if name in widgets_data:
            w.setToolTip(
                widgets_data[name].get(
                    locale,
                    widgets_data[name].get('ar', ''),
                )
            )
        else:
            translated = _translate_text(tip, locale)
            if translated:
                w.setToolTip(translated)


def apply_widget_texts(dialog, locale: str) -> None:
    """Set text on all children of dialog using widgets.json data."""
    widgets_data = _load_widgets()
    _translate_labels(dialog, locale, widgets_data)
    _translate_groupbox(dialog, locale, widgets_data)
    _translate_placeholder(dialog, locale)
    _translate_tabs(dialog, locale)
    _translate_window_title(dialog, locale)
    _translate_tooltips(dialog, locale, widgets_data)
