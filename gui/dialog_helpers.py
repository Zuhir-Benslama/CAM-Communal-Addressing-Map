"""Shared helpers for dialog UI construction."""

from types import SimpleNamespace

from qgis.PyQt.QtWidgets import QLabel, QVBoxLayout, QWidget


class _SimpleTabBar:
    """Minimal tab-like facade for mixin compatibility."""

    def __init__(self) -> None:
        self._current = 0
        self._names = {0: 'Operations', 1: 'Report', 2: 'Settings'}

    def setCurrentIndex(self, index: int) -> None:
        self._current = index

    def currentIndex(self) -> int:
        return self._current

    def tabText(self, index: int) -> str:
        return self._names.get(index, '')

    def count(self) -> int:
        return len(self._names)

    def currentWidget(self) -> SimpleNamespace:
        idx = self.currentIndex()
        return SimpleNamespace(
            objectName=lambda: 'tab_ops' if idx == 0 else 'tab',
        )

    def tabBar(self) -> SimpleNamespace:
        return SimpleNamespace(hide=lambda: None)

    @staticmethod
    def setDocumentMode(val: bool) -> None:
        pass

    @staticmethod
    def setUsesScrollButtons(val: bool) -> None:
        pass

    @staticmethod
    def setStyleSheet(ss: str) -> None:
        pass


def make_section_frame(max_width: int | None = None) -> QWidget:
    w = QWidget()
    w.setObjectName('sectionFrame')
    if max_width is not None:
        w.setMaximumWidth(max_width)
    layout = QVBoxLayout(w)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)
    return w


def add_form_row(form, label_text: str, obj_name: str, field) -> QLabel:
    label = QLabel(label_text)
    label.setObjectName(obj_name)
    form.addRow(label, field)
    return label
