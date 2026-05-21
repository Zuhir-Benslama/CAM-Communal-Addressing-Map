"""Main plugin entry point for the RNA QGIS plugin."""
import os
import logging
from typing import Any

from qgis.PyQt.QtCore import QSettings, QCoreApplication, Qt, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QMessageBox
from qgis.core import QgsApplication

from ..gui.main_dialog import RNADialog
from ..shared.constants import (
    ICON_PNG, SETTINGS_ORG, SETTINGS_APP, SETTINGS_KEY_LOCALE,
)
from ..shared.utils import current_locale
from ..scripts.lookup_data import get_string

logger = logging.getLogger(__name__)


class RNA:
    def __init__(self, iface) -> None:
        QgsApplication.setPrefixPath(os.getenv('QGIS_BASE_PATH', '/usr'), True)

        svg_path = os.path.join(
            os.getenv('QGIS_BASE_PATH', '/usr'),
            'apps', 'qgis', 'svg'
        )
        QgsApplication.setDefaultSvgPaths([svg_path])
        QgsApplication.instance().setSvgPaths([svg_path])

        self.iface = iface
        self.plugin_dir = os.path.dirname(os.path.dirname(__file__))
        settings = QSettings()
        settings.beginGroup('digitizing')
        settings.setValue('disable-enter-attribute-values-dialog', True)
        settings.endGroup()

        self._locale_code = QSettings(SETTINGS_ORG, SETTINGS_APP).value(
            SETTINGS_KEY_LOCALE, '')
        if not self._locale_code:
            locale_val = QSettings().value('locale/userLocale')
            self._locale_code = locale_val[0:2] if locale_val else 'en'

        self.actions = []
        self.menu = self.tr('&RNA')
        self.first_start = None

    def tr(self, message) -> str:
        return QCoreApplication.translate('RNA', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ) -> Any:
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self) -> None:
        self.add_action(
            ICON_PNG,
            text=self.tr(''),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )
        self.first_start = True

    def unload(self) -> None:
        for action in self.actions:
            self.iface.removePluginMenu(self.tr('&RNA'), action)
            self.iface.removeToolBarIcon(action)

    def run(self) -> None:
        logger.info("run() called, first_start=%s", self.first_start)

        if self.first_start is True:
            self.first_start = False
            try:
                self.dlg = RNADialog(self.iface)
                logger.info("RNADialog created successfully")
            except Exception as e:
                logger.exception("Failed to create RNADialog: %s", e)
                loc = current_locale()
                QMessageBox.critical(
                    None, get_string("RNA Plugin Error", loc),
                    get_string("Failed to create dialog", loc) + "\n\n"
                    + get_string("Check the QGIS log for details.", loc),
                )
                return

            loc = current_locale()
            self.dock_widget = QDockWidget(
                get_string("RNA Plugin", loc), self.iface.mainWindow()
            )
            self.dock_widget.setWidget(self.dlg)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)
            self.dock_widget.show()
            QTimer.singleShot(0, self._normalize_dock_width)

        if hasattr(self, 'dock_widget'):
            self._normalize_dock_width()
            self.dock_widget.raise_()
            self.dock_widget.show()
            QTimer.singleShot(0, self._normalize_dock_width)

    def _normalize_dock_width(self) -> None:
        if not hasattr(self, 'dock_widget'):
            return

        default_width = 680
        min_width = 580
        max_width = 920

        self.dock_widget.setMinimumWidth(min_width)
        self.dock_widget.setMaximumWidth(max_width)
        if (self.dock_widget.width() > 760
                or self.dock_widget.width() < min_width):
            self.dock_widget.resize(default_width, self.dock_widget.height())
