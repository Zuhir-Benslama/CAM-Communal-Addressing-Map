"""Authentication and login flow mixin for user management."""

from __future__ import annotations

import logging

from qgis.core import QgsProject, QgsRasterLayer
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QWidget

from ..app.users.repository import get_current_user, qgis_config
from ..app.users.service import logout, sign_in, sign_up
from ..constants import current_theme, get_dialog_qss, validate_text
from ..gui.ui_fillers import (
    fill_activity_type,
    fill_commune_of_wilaya,
    fill_org_type,
)
from ..layer.refresh import refresh_all_layers
from ..layer.utils import init_allowed_zone
from ._protocols import (
    HasAuthContext,
    HasCategoryWidgets,
    HasFullAuthContext,
    HasLocationWidgets,
    HasMapOptionWidgets,
    HasNavWidgets,
    HasTranslation,
)

logger = logging.getLogger(__name__)


class AuthMixin:
    """Mixin handling user authentication, registration, and session
    management."""

    def _show_error(self: HasTranslation, text: str) -> None:
        """Show a critical error message dialog."""
        QMessageBox.critical(self, self._tr("Error"), text)

    def _show_info(self: HasTranslation, text: str) -> None:
        """Show an informational success message dialog."""
        QMessageBox.information(self, self._tr("Success"), text)

    def submit_add_usr(self: HasAuthContext) -> None:
        """Register a new user via the sign-up API."""
        current_index = self.commune_of_wilaya.currentIndex()
        selected_value = self.commune_of_wilaya.itemData(current_index)
        ok, errors = sign_up(
            username=validate_text(self.uname.text()),
            password=validate_text(self.pwd.text()),
            email=validate_text(self.email.text()),
            first_name=validate_text(self.fname.text()),
            lastname=validate_text(self.lname.text()),
            phone=validate_text(self.pnum.text()),
            commune_code=selected_value,
        )
        if ok:
            self.public_route('login')
        elif errors:
            self._show_error("\n".join(errors))

    def login_user(
        self: HasFullAuthContext,
    ) -> None:
        """Authenticate the user and initialize the map session on success."""
        ok, username, error = sign_in(
            username=validate_text(self.username.text()),
            password=validate_text(self.password.text()),
        )
        if ok and username:
            self.label_username.setText(username)
            indicator = self.add_map_layer()
            if indicator:
                self.current_user = get_current_user()
                if not self._load_map_data():
                    return
                self.private_route('main')
                self.menu.setCurrentIndex(0)
                self.on_opt_selected(0)
            else:
                self._show_error(
                    self._tr("Unable to log in to server or image not found"),
                )
        elif error:
            self._show_error(error)

    def _load_map_data(self: HasFullAuthContext) -> bool:
        """Load zone and layers for the authenticated user."""
        try:
            init_allowed_zone(self.iface)
            refresh_all_layers(self.iface)
            return True
        except Exception as e:  # pylint: disable=W0718
            logger.error("Error loading map data after login: %s", e)
            self._show_error(self._tr(f"Error loading map: {e}"))
            return False

    def fill_map_options(self: HasMapOptionWidgets) -> None:
        """Populate the map options combo box from QGIS config."""
        maps = qgis_config().get('map_layers') or []
        self.map_options.clear()
        for cfg in maps:
            self.map_options.addItem(cfg.get('label'), cfg.get('url'))

    def add_map_layer(self: HasFullAuthContext) -> bool:
        """Add the selected raster or WMS map layer to the project."""
        selected_label = self.map_options.currentText()
        selected_value = self.map_options.currentData()
        logger.info("add_map_layer: label=%r value=%r items=%d index=%d",
                     selected_label, selected_value,
                     self.map_options.count(), self.map_options.currentIndex())

        if selected_value and selected_label:
            if selected_label.startswith('Satellite View '):
                osm_layer = QgsRasterLayer(
                    selected_value, selected_label, "wms",
                )
                if osm_layer.isValid():
                    existing_layers = (
                        QgsProject.instance().mapLayersByName(selected_label)
                    )
                    if existing_layers:
                        self.sat_view = selected_label
                        self.rast = None
                        return True
                    QgsProject.instance().addMapLayer(osm_layer)
                    self.sat_view = selected_label
                    self.rast = None
                    return True

            if selected_label == 'Raster':
                dialog = QFileDialog(self, self._tr("Select a file"))
                dialog.setOption(QFileDialog.DontUseNativeDialog, True)
                dialog.setNameFilter("TIFF Files (*.tif *.tiff)")
                dialog.setFileMode(QFileDialog.ExistingFile)
                self.sat_view = None
                self.rast = selected_label
                dialog.setStyleSheet(get_dialog_qss(current_theme()))

                if dialog.exec():
                    selected_file = dialog.selectedFiles()[0]
                    logger.info("Selected file: %s", selected_file)
                    if selected_file:
                        raster_layer = QgsRasterLayer(
                            selected_file, selected_label,
                        )
                        if raster_layer.isValid():
                            QgsProject.instance().addMapLayer(raster_layer)
                            return True
                        return False
                    return False
                return False
            QMessageBox.critical(
                self, self._tr("Error"), self._tr("Failed to Map layer.")
            )
        else:
            QMessageBox.warning(
                self,
                self._tr("No Selection"),
                self._tr("Please select a map layer option."),
            )
        return False

    def private_route(self: HasNavWidgets, page_index) -> None:
        """Navigate to a private (authenticated) page in the stacked widget."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)

    def public_route(self: HasNavWidgets, page_index) -> None:
        """Navigate to a public (login/register) page in the stacked widget."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)

    def closeEvent(
        self: HasFullAuthContext, event,
    ) -> None:
        """Clean up tools and logout on dialog close."""
        self.stop()
        self.sat_view = None
        self.rast = None
        if self.identify_tool:
            logout(iface=self.iface, dlg=self.identify_tool.dlg)
        else:
            logout(iface=self.iface, dlg=None)

        if self.popup_dialog:
            self.popup_dialog.close()
        page = self.router.findChild(QWidget, "login")
        if page:
            self.router.setCurrentWidget(page)
        event.accept()

    def on_select_wilaya(self: HasLocationWidgets, _index) -> None:
        """Populate the commune combo when the wilaya selection changes."""
        selected_value = self.wilaya_list.itemData(
            self.wilaya_list.currentIndex(),
        )
        fill_commune_of_wilaya(self.commune_of_wilaya, selected_value)

    def on_select_org_cat(self: HasCategoryWidgets, _index) -> None:
        """Populate the organization type combo when the category changes."""
        selected_value = self.org_cat.itemData(self.org_cat.currentIndex())
        fill_org_type(self.org_type, selected_value)

    def on_select_activity_cat(self: HasCategoryWidgets, _index) -> None:
        """Populate the activity type combo when the category changes."""
        selected_value = self.activity_cat.itemData(self.activity_cat.currentIndex())
        fill_activity_type(self.activity_type, selected_value)
