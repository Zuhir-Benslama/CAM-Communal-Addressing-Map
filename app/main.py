"""Main plugin entry point for the CAM QGIS plugin."""

import logging
import os
from pathlib import Path
from typing import Any

from qgis.core import QgsApplication
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QCoreApplication, QSettings, Qt, QTimer
from qgis.PyQt.QtGui import QAction, QIcon
from qgis.PyQt.QtWidgets import QDockWidget, QMessageBox

from ..gui.main_dialog import MainDialog
from ..scripts.widget_texts import get_string
from .shared.constants import (
    ICON_PNG,
    SETTINGS_APP,
    SETTINGS_KEY_LOCALE,
    SETTINGS_ORG,
)
from .shared.utils import current_locale

logger = logging.getLogger(__name__)


class CAM:
    """Main plugin class — handles startup, GUI creation, and teardown."""

    def __init__(self, iface: QgisInterface) -> None:
        QgsApplication.setPrefixPath(os.getenv('QGIS_BASE_PATH', '/usr'), True)

        svg_path = str(
            Path(os.getenv('QGIS_BASE_PATH', '/usr')) / 'apps' / 'qgis' / 'svg'
        )
        QgsApplication.setDefaultSvgPaths([svg_path])
        QgsApplication.instance().setSvgPaths([svg_path])

        self.iface: QgisInterface = iface
        self.plugin_dir: str = str(Path(__file__).resolve().parent.parent)
        settings = QSettings()
        settings.beginGroup('digitizing')
        settings.setValue('disable-enter-attribute-values-dialog', True)
        settings.endGroup()

        self._locale_code: str = QSettings(SETTINGS_ORG, SETTINGS_APP).value(
            SETTINGS_KEY_LOCALE, ''
        )
        if not self._locale_code:
            locale_val = QSettings().value('locale/userLocale')
            self._locale_code = locale_val[0:2] if locale_val else 'en'

        self.actions: list[QAction] = []
        self.menu: str = self.tr('&CAM')
        self.first_start: bool | None = None

    def tr(self, message: str) -> str:
        """Translate *message* via Qt's internationalisation framework."""
        return QCoreApplication.translate('CAM', message)

    def add_action(
        self,
        icon_path: str,
        text: str,
        callback: object,
        *,
        enabled_flag: bool = True,
        add_to_menu: bool = True,
        add_to_toolbar: bool = True,
        status_tip: str | None = None,
        whats_this: str | None = None,
        parent: Any = None,
    ) -> Any:
        """Register a QGIS toolbar action and/or menu item."""
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
        """Create the plugin toolbar button and menu entry."""
        self.add_action(
            str(ICON_PNG),
            text=self.tr('CAM'),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )
        self.first_start = True

    def unload(self) -> None:
        """Remove all plugin toolbar buttons and menu entries."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr('&CAM'), action)
            self.iface.removeToolBarIcon(action)

    def run(self) -> None:
        """Launch (or raise) the plugin dock widget."""
        logger.info('run() called, first_start=%s', self.first_start)

        if self.first_start is True:
            self.first_start = False
            try:
                self.dlg = MainDialog(self.iface)
                logger.info('MainDialog created successfully')
            except Exception:  # pylint: disable=W0718
                logger.exception('Failed to create MainDialog')
                loc = current_locale()
                QMessageBox.critical(
                    None,
                    get_string('CAM Plugin Error', loc),
                    get_string('Failed to create dialog', loc)
                    + '\n\n'
                    + get_string('Check the QGIS log for details.', loc),
                )
                return

            loc = current_locale()
            self.dock_widget: QDockWidget = QDockWidget(
                get_string('CAM Plugin', loc), self.iface.mainWindow()
            )
            self.dock_widget.setWidget(self.dlg)
            self.iface.addDockWidget(
                Qt.DockWidgetArea.LeftDockWidgetArea,
                self.dock_widget,
            )
            self.dock_widget.show()
            QTimer.singleShot(0, self._normalize_dock_width)

        if hasattr(self, 'dock_widget'):
            self._normalize_dock_width()
            self.dock_widget.raise_()
            self.dock_widget.show()
            QTimer.singleShot(0, self._normalize_dock_width)

    def _normalize_dock_width(self) -> None:
        """Constrain dock widget width within acceptable bounds."""
        if not hasattr(self, 'dock_widget'):
            return

        default_width = 680
        min_width = 580

        self.dock_widget.setMinimumWidth(min_width)
        if self.dock_widget.width() > 760 or self.dock_widget.width() < min_width:
            self.dock_widget.resize(default_width, self.dock_widget.height())
