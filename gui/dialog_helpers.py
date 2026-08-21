"""Shared helpers for dialog UI construction."""

from dataclasses import dataclass

from qgis.PyQt.QtWidgets import QFormLayout, QLabel, QVBoxLayout, QWidget


@dataclass
class _TabWidget:
    """Lightweight tab state tracker for mixin compatibility.

    Stores the current tab index and provides a ``QTabWidget``-like
    interface for mixins that need to know which tab is active.
    """

    _current: int = 0
    _names: tuple[str, str, str] = ('Operations', 'Report', 'Settings')

    def setCurrentIndex(self, index: int) -> None:
        self._current = index

    def currentIndex(self) -> int:
        return self._current

    def tabText(self, index: int) -> str:
        return self._names[index] if 0 <= index < len(self._names) else ''

    def count(self) -> int:
        return len(self._names)

    @property
    def currentWidget(self) -> str:
        return 'tab_ops' if self._current == 0 else 'tab'


def make_section_frame(max_width: int | None = None) -> QWidget:
    w = QWidget()
    w.setObjectName('sectionFrame')
    if max_width is not None:
        w.setMaximumWidth(max_width)
    layout = QVBoxLayout(w)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)
    return w


def add_form_row(
    form: QFormLayout,
    label_text: str,
    obj_name: str,
    field: QWidget,
) -> QLabel:
    label = QLabel(label_text)
    label.setObjectName(obj_name)
    form.addRow(label, field)
    return label
