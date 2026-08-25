"""Paginated dialog for browsing entity records — Qt Widgets version."""

from __future__ import annotations

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.shared.utils import get_all_fields_and_labels, locale_value
from ..constants import current_locale, current_theme
from ..scripts.widget_texts import apply_widget_texts, get_string


class EntityListDialog(QDialog):
    """Paginated dialog displaying a table of entity records."""

    PAGE_SIZE = 50

    def __init__(self, model_name: str, list_of: str, parent=None) -> None:
        super().__init__(parent)

        self.model_name = model_name
        self._list_of = list_of
        self._page = 0
        self._total_records = 0
        self._tr_locale = current_locale()

        self._init_ui()
        self.setStyleSheet(get_theme_qss(current_theme()))

        apply_widget_texts(self, self._tr_locale)
        title = (
            get_string('List', self._tr_locale)
            + ' '
            + get_string(list_of, self._tr_locale)
        )
        self.setWindowTitle(title)
        self._populate_table(0)

    def _init_ui(self) -> None:
        self.setObjectName('camEntityListDialog')
        self.setMinimumSize(700, 520)
        self.resize(760, 560)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._table = QTableWidget()
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        layout.addWidget(self._table, stretch=1)

        pagination = QHBoxLayout()
        self._btn_prev = QPushButton()
        self._btn_prev.setMaximumWidth(200)
        self._btn_prev.clicked.connect(self._on_prev)
        pagination.addWidget(self._btn_prev)

        self._label_page = QLabel()
        self._label_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination.addWidget(self._label_page, stretch=1)

        self._btn_next = QPushButton()
        self._btn_next.setMaximumWidth(200)
        self._btn_next.clicked.connect(self._on_next)
        pagination.addWidget(self._btn_next)

        layout.addLayout(pagination)

    def _on_prev(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._populate_table(self._page)

    def _on_next(self) -> None:
        if (self._page + 1) * self.PAGE_SIZE < self._total_records:
            self._page += 1
            self._populate_table(self._page)

    def _populate_table(self, page: int) -> None:
        """Query DB for the given page and populate the table."""
        session = get_session()
        try:
            model_class = getattr(_models, self.model_name, None)
            if model_class is None:
                self._total_records = 0
                self._table.setRowCount(0)
                self._table.setColumnCount(0)
                self._update_pagination()
                return

            self._total_records = session.query(model_class).count()

            offset = page * self.PAGE_SIZE
            results = (
                session.query(model_class).offset(offset).limit(self.PAGE_SIZE).all()
            )

            property_labels = {
                'label': 'Label',
                'username': 'User',
            }

            fields, labels = get_all_fields_and_labels(
                model_class, property_labels, locale=self._tr_locale
            )

            labels = [
                get_string(label, self._tr_locale)
                if any('\u0600' <= c <= '\u06ff' for c in label)
                else label
                for label in labels
            ]

            self._table.setColumnCount(len(fields))
            self._table.setHorizontalHeaderLabels(labels)
            self._table.setRowCount(len(results))

            for row_idx, record in enumerate(results):
                for col_idx, field in enumerate(fields):
                    try:
                        value: object = locale_value(record, field, self._tr_locale)
                    except AttributeError:
                        value = getattr(record, field, None)
                    value = value if value not in (None, '') else 'N/A'
                    item = QTableWidgetItem(str(value))
                    self._table.setItem(row_idx, col_idx, item)

            self._table.horizontalHeader().setStretchLastSection(True)
            self._table.resizeColumnsToContents()

            self._update_pagination()
        finally:
            session.close()

    def _update_pagination(self) -> None:
        total_pages = max(
            1, (self._total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        )
        current = self._page + 1
        self._label_page.setText(f'{current} / {total_pages}')
        self._btn_prev.setEnabled(self._page > 0)
        self._btn_next.setEnabled(
            (self._page + 1) * self.PAGE_SIZE < self._total_records
        )
