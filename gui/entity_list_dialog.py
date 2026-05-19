"""Paginated dialog for browsing entity records."""
import os
import logging

from .. import models as _models
from ..models import get_session, get_all_fields_and_labels
from ..constants import (
    current_theme, get_theme_qss,
    SETTINGS_ORG, SETTINGS_APP, SETTINGS_KEY_LOCALE,
    current_locale, locale_value,
)
from ..scripts.lookup_data import get_string, apply_widget_texts

from PyQt5 import uic
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QDialog, QTableWidgetItem, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QWidget
)

logger = logging.getLogger(__name__)


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'liste.ui'))


class EntityListDialog(QDialog, FORM_CLASS):
    """Paginated dialog displaying a table of entity records."""
    PAGE_SIZE = 50

    def __init__(self, model_name: str, list_of: str,
                 parent: object = None) -> None:
        """Initialize the list dialog with paginated table."""

        self.model_name = model_name
        self._page = 0
        self._total_records = 0

        s = QSettings(SETTINGS_ORG, SETTINGS_APP)
        locale = s.value(SETTINGS_KEY_LOCALE, '')
        if not locale:
            locale_val = QSettings().value('locale/userLocale')
            locale = locale_val[0:2] if locale_val else 'en'
        self._tr_locale = locale

        super(EntityListDialog, self).__init__(parent)
        self.setupUi(self)
        apply_widget_texts(self, self._tr_locale)
        self.setStyleSheet(get_theme_qss(current_theme()))

        self.list_title.setText("\u200f " + get_string("  قائمة ", self._tr_locale) + "\u200f " + get_string(list_of, self._tr_locale))

        self._prev_btn = QPushButton(get_string("السابق", self._tr_locale))
        self._next_btn = QPushButton(get_string("التالي", self._tr_locale))
        self._page_label = QLabel()

        self._prev_btn.clicked.connect(self._prev_page)
        self._next_btn.clicked.connect(self._next_page)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self._prev_btn)
        button_layout.addWidget(self._page_label)
        button_layout.addWidget(self._next_btn)

        container = QWidget()
        container.setLayout(button_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.layout().addLayout(main_layout)

        self.populate_table()

    def _prev_page(self) -> None:
        """Go to the previous page of results."""
        if self._page > 0:
            self._page -= 1
            self.populate_table()

    def _next_page(self) -> None:
        """Go to the next page of results."""
        if (self._page + 1) * self.PAGE_SIZE < self._total_records:
            self._page += 1
            self.populate_table()

    def populate_table(self) -> None:
        """Populate the table with the current page of records."""
        session = get_session()
        try:
            model_class = getattr(_models, self.model_name, None)
            if model_class is None:
                return

            self._total_records = session.query(model_class).count()
            total_pages = max(
                1, (self._total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
            self._page_label.setText(
                get_string("الصفحة", self._tr_locale) + f" {self._page + 1} / {total_pages}")

            offset = self._page * self.PAGE_SIZE
            results = (
                session.query(model_class)
                .offset(offset).limit(self.PAGE_SIZE).all()
            )

            PROPERTY_LABELS = {
                'pan_label': 'تسمية',
                'username': 'مستخدم',
            }

            fields, labels = get_all_fields_and_labels(
                model_class, PROPERTY_LABELS, locale=self._tr_locale)

            labels = [get_string(l, self._tr_locale) if any('\u0600' <= c <= '\u06FF' for c in l) else l
                      for l in labels]

            self.table.setRowCount(len(results))
            self.table.setColumnCount(len(fields))
            self.table.setHorizontalHeaderLabels(labels)

            for row_index, record in enumerate(results):
                for col_index, field in enumerate(fields):
                    try:
                        value = locale_value(record, field, self._tr_locale)
                    except Exception:
                        try:
                            value = getattr(record, field)
                        except Exception:
                            logger.debug(
                                "Field %s not found on record %s",
                                field, record, exc_info=True
                            )
                            value = 'N/A'
                    value = value if value not in [None, ""] else "N/A"
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_index, col_index, item)

            self._prev_btn.setEnabled(self._page > 0)
            self._next_btn.setEnabled(
                (self._page + 1) * self.PAGE_SIZE < self._total_records)
        finally:
            session.close()


