"""Paginated dialog for browsing entity records — QML version."""

from __future__ import annotations

import logging
import os
from typing import Any

from qgis.PyQt.QtCore import QObject, QUrl, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout

try:
    from qgis.PyQt.QtQuickWidgets import QQuickWidget

    _HAS_QML = True
except ImportError:
    QQuickWidget = None
    _HAS_QML = False

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.shared.utils import get_all_fields_and_labels
from ..constants import current_locale, current_theme
from ..scripts.lookup_data import apply_widget_texts, get_string

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QML_DIR = os.path.join(PLUGIN_DIR, 'qml')


class EntityListBridge(QObject):
    """Bridge object exposed to QML for Python <-> QML communication."""

    def __init__(self, dialog: EntityListDialog) -> None:
        super().__init__()
        self.dialog = dialog
        self._page = 0
        self._page_size = 50
        self._total_records = 0

    @pyqtSlot(int)
    def loadPage(self, page: int) -> None:
        self.dialog.populate_table(page)

    @pyqtSlot()
    def nextPage(self) -> None:
        if (self._page + 1) * self._page_size < self._total_records:
            self._page += 1
            self.loadPage(self._page)

    @pyqtSlot()
    def prevPage(self) -> None:
        if self._page > 0:
            self._page -= 1
            self.loadPage(self._page)

    def set_page_state(self, page: int, total: int) -> None:
        self._page = page
        self._total_records = total


class EntityListDialog(QDialog):
    """Paginated dialog displaying a table of entity records (QML-backed)."""

    PAGE_SIZE = 50

    def __init__(self, model_name: str, list_of: str, parent=None) -> None:
        super().__init__(parent)

        self.model_name = model_name
        self._list_of = list_of
        self._page = 0
        self._total_records = 0
        self._tr_locale = current_locale()

        self._init_qml()
        self.setStyleSheet(get_theme_qss(current_theme()))

        apply_widget_texts(self, self._tr_locale)
        title = (
            get_string('List', self._tr_locale)
            + ' '
            + get_string(list_of, self._tr_locale)
        )
        self.setWindowTitle(title)
        self._populate_table(0)

    def _init_qml(self) -> None:  # pylint: disable=duplicate-code
        if not _HAS_QML or QQuickWidget is None:
            raise ImportError(
                'Qt Quick Widgets (QtQml) is not available.\n'
                'Please install the Qt Quick / QML package for your system\n'
                '(e.g., python3-pyqt6.qml or qml6 on Debian/Ubuntu).'
            )
        self.setObjectName('rnaEntityListDialog')
        self.setMinimumSize(700, 520)
        self.resize(760, 560)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._quick_widget = QQuickWidget()
        self._quick_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)

        engine = self._quick_widget.engine()
        engine.addImportPath(QML_DIR)
        for p in (
            '/usr/lib64/qt5/qml',
            '/usr/lib/qt5/qml',
        ):
            if os.path.isdir(p):
                engine.addImportPath(p)

        self._bridge = EntityListBridge(self)
        context = self._quick_widget.rootContext()
        context.setContextProperty('pluginBridge', self._bridge)
        context.setContextProperty(
            'listTitle', get_string(self._list_of, self._tr_locale)
        )
        context.setContextProperty('isDark', current_theme() == 'dark')
        context.setContextProperty('isRTL', self._tr_locale == 'ar')

        qml_path = os.path.join(QML_DIR, 'entitylist', 'EntityListDialog.qml')
        self._quick_widget.setSource(QUrl.fromLocalFile(qml_path))

        layout.addWidget(self._quick_widget)

        self._qml_root = self._quick_widget.rootObject()

    def _populate_table(self, page: int) -> None:
        """Query DB for the given page and push data to QML."""
        session = get_session()
        try:
            model_class = getattr(_models, self.model_name, None)
            if model_class is None:
                self._total_records = 0
                self._bridge.set_page_state(page, 0)
                self._qml_root.setPageData(
                    {
                        'fields': [],
                        'labels': [],
                        'rows': [],
                        'total': 0,
                        'page': 0,
                        'pageSize': self.PAGE_SIZE,
                    }
                )
                return

            self._total_records = session.query(model_class).count()

            offset = page * self.PAGE_SIZE
            results = (
                session.query(model_class).offset(offset).limit(self.PAGE_SIZE).all()
            )

            PROPERTY_LABELS = {
                'pan_label': 'Label',
                'username': 'User',
            }

            fields, labels = get_all_fields_and_labels(
                model_class, PROPERTY_LABELS, locale=self._tr_locale
            )

            labels = [
                get_string(label, self._tr_locale)
                if any('\u0600' <= c <= '\u06ff' for c in label)
                else label
                for label in labels
            ]

            rows = []
            for record in results:
                row = []
                for field in fields:
                    try:
                        from ..app.shared.utils import locale_value

                        value: Any = locale_value(record, field, self._tr_locale)
                    except AttributeError:
                        value = getattr(record, field, None)
                    value = value if value not in (None, '') else 'N/A'
                    row.append(value)
                rows.append(row)

            self._bridge.set_page_state(page, self._total_records)

            self._qml_root.setPageData(
                {
                    'fields': fields,
                    'labels': labels,
                    'rows': rows,
                    'total': self._total_records,
                    'page': page,
                    'pageSize': self.PAGE_SIZE,
                }
            )
        finally:
            session.close()

    def populate_table(self, page: int | None = None) -> None:
        """Public API: populate the table (compat wrapper)."""
        if page is None:
            page = self._page
        self._populate_table(page)
