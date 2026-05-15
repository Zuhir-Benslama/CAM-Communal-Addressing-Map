"""Authentication and login flow mixin for user management."""

import logging


from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog, QWidget
from qgis.core import QgsProject, QgsRasterLayer

from ..auth.operations import sign_up, sign_in, logout
from ..models import get_current_user
from ..layer.utils import init_allowed_zone
from ..layer.refresh import refresh_all_layers
from ..db.operations import qgis_config
from ..constants import validate_text, current_theme, get_dialog_qss

logger = logging.getLogger(__name__)


class AuthMixin:
    """Mixin handling user authentication, registration, and session
    management."""

    def submit_add_usr(self) -> None:
        """Register a new user via the sign-up API."""
        current_index = self.commune_of_wilaya.currentIndex()
        selected_value = self.commune_of_wilaya.itemData(current_index)
        ok = sign_up(
            username=validate_text(self.uname.text()),
            password=validate_text(self.pwd.text()),
            email=validate_text(self.email.text()),
            first_name=validate_text(self.fname.text()),
            lastname=validate_text(self.lname.text()),
            phone=validate_text(self.pnum.text()),
            affectation_id=selected_value,
        )
        if ok:
            self.public_route('login')

    def login_user(self) -> None:
        """Authenticate the user and initialize the map session on success."""
        flag = sign_in(
            username=validate_text(self.username.text()),
            password=validate_text(self.password.text()),
            label=self.label_username,
        )
        if flag:
            indicator = self.add_map_layer()
            if indicator:
                init_allowed_zone(self.iface)
                refresh_all_layers(self.iface)
                self.private_route('main')
                self.menu.setCurrentIndex(0)
                self.on_opt_selected(0)
                self.current_user = get_current_user()
            else:
                QMessageBox.critical(
                    self, "Error",
                    "غير قادر على تسجيل الدخول إلى الخادم أو الصورة غير موجودة",
                )

    def fill_map_options(self) -> None:
        """Populate the map options combo box from QGIS config."""
        maps = qgis_config().get('map_layers')
        self.map_options.clear()
        for m in maps:
            self.map_options.addItem(m.get('label'), m.get('url'))

    def add_map_layer(self) -> bool:
        """Add the selected raster or WMS map layer to the project."""
        selected_label = self.map_options.currentText()
        selected_value = self.map_options.currentData()

        if selected_value and selected_label:
            if selected_label.startswith('Satellite View '):
                osm_layer = QgsRasterLayer(
                    selected_value, selected_label, "wms",
                )
                if osm_layer.isValid():
                    existing_layers = (
                        QgsProject.instance().mapLayersByName(selected_label)
                    )
                    if not existing_layers:
                        QgsProject.instance().addMapLayer(osm_layer)
                        self.sat_view = selected_label
                        self.rest = None
                        return True

            if selected_label == 'Raster':
                dialog = QFileDialog(self, "Select a file")
                dialog.setOption(QFileDialog.DontUseNativeDialog, True)
                dialog.setNameFilter("TIFF Files (*.tif *.tiff)")
                dialog.setFileMode(QFileDialog.ExistingFile)
                self.sat_view = None
                self.rast = selected_label
                dialog.setStyleSheet(get_dialog_qss(current_theme()))

                if dialog.exec_():
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
            QMessageBox.critical(self, "Error", "Failed to Map layer.")
        else:
            QMessageBox.warning(
                self, "No Selection", "Please select a map layer option.",
            )
        return False

    def private_route(self, page_index) -> None:
        """Navigate to a private (authenticated) page in the stacked widget."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)

    def public_route(self, page_index) -> None:
        """Navigate to a public (login/register) page in the stacked widget."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)

    def closeEvent(self, event) -> None:
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

    def on_select_wilaya(self, index) -> None:
        """Populate the commune combo when the wilaya selection changes."""
        from ..gui.ui_fillers import fill_commune_of_wilaya
        selected_value = self.wilaya_list.itemData(
            self.wilaya_list.currentIndex(),
        )
        fill_commune_of_wilaya(self.commune_of_wilaya, selected_value)

    def on_select_catOrg(self, index) -> None:
        """Populate the organization type combo when the category changes."""
        from ..gui.ui_fillers import fill_type_org
        selected_value = self.cat_org.itemData(self.cat_org.currentIndex())
        fill_type_org(self.type_org, selected_value)

    def on_select_newCatOrg(self, index) -> None:
        """Populate the new org type combo when the new category changes."""
        from ..gui.ui_fillers import fill_type_org
        selected_value = self.new_cat_org.itemData(
            self.new_cat_org.currentIndex(),
        )
        fill_type_org(self.new_type_org, selected_value)

    def on_select_newCatAct(self, index) -> None:
        """Populate the new activity type combo when the new category
        changes."""
        from ..gui.ui_fillers import fill_type_act
        selected_value = self.new_cat_act.itemData(
            self.new_cat_act.currentIndex(),
        )
        fill_type_act(self.new_type_act, selected_value)

    def on_select_catAct(self, index) -> None:
        """Populate the activity type combo when the category changes."""
        from ..gui.ui_fillers import fill_type_act
        selected_value = self.cat_act.itemData(self.cat_act.currentIndex())
        fill_type_act(self.type_act, selected_value)
