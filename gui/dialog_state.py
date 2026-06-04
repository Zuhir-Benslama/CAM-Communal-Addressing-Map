"""Dialog state management — theme/locale, combo population, translation.

Each function takes a dialog instance as its first argument and operates
on its attributes directly (matching the mixin pattern).
"""

from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtWidgets import QApplication, QFileDialog

from ..constants import (
    AVAILABLE_LOCALES,
    DEFAULT_THEME,
    SETTINGS_APP,
    SETTINGS_KEY_LOCALE,
    SETTINGS_KEY_THEME,
    SETTINGS_ORG,
    THEME_DARK,
    THEME_LIGHT,
    get_theme_qss,
)
from ..scripts.widget_texts import (
    apply_widget_texts,
    clear_i18n_cache,
    get_string,
)
from .ui_fillers import (
    fill_activity_category,
    fill_feature_combo,
    fill_mounting_status,
    fill_numbering_state,
    fill_org_category,
    fill_panel_reference,
    fill_paper,
    fill_road_reference,
    fill_road_type,
    fill_subdivision_type,
    fill_wilayas_list,
    fill_zone_type,
)

ARABIC_ACTION_NAMES = {
    'report': 'تقرير',
    'order': 'نموذج طلبية',
    'panels_map': 'إنشاء خريطة اللوحات',
    'num_map': 'إنشاء خريطة الترقيم',
    'backup': 'إنشاء نسخة احتياطية لقاعدة البيانات',
}

ARABIC_THEME_NAMES = {
    'dark': 'داكن',
    'light': 'فاتح',
}

LOCALE_LABELS = {
    'ar': {'ar': 'العربية', 'fr': 'Arabe', 'en': 'Arabic'},
    'fr': {'ar': 'الفرنسية', 'fr': 'Français', 'en': 'French'},
    'en': {'ar': 'الإنجليزية', 'fr': 'Anglais', 'en': 'English'},
}

LAYER_TRANSLATIONS = {
    'Zones': 'المناطق',
    'Roads': 'الطرق',
    'Facilities': 'المرافق',
    'Subdivisions': 'التجزئات',
    'Numbering': 'الترقيم',
    'Panels': 'اللوحات',
}


def populate_combos(dialog) -> None:
    loc = dialog._tr_locale
    for name in dialog.LAYER_INDEX_MAP:
        dialog._combo_layer_selector.addItem(
            get_string(LAYER_TRANSLATIONS[name], loc), name
        )
    for label, data in ARABIC_ACTION_NAMES.items():
        dialog._combo_action.addItem(get_string(data, loc), label)
    fill_paper(dialog._combo_paper)
    fill_wilayas_list(dialog.wilaya_list)
    fill_road_type(dialog._combo_type_road)
    fill_numbering_state(dialog._combo_num_state)
    fill_mounting_status(dialog._combo_mount_status)
    fill_subdivision_type(dialog._combo_subd_type)
    fill_zone_type(dialog._combo_zone_type)
    fill_road_reference(dialog._combo_road_ref)
    fill_panel_reference(dialog._combo_panel_ref)
    fill_feature_combo(dialog.feature_combo)
    fill_org_category(dialog._combo_org_cat)
    fill_activity_category(dialog._combo_activity_cat)
    dialog._on_feature_changed(dialog.feature_combo.currentIndex())
    dialog._update_action_button_texts(dialog._combo_layer_selector.currentIndex())


def translate_internal_combos(dialog) -> None:
    loc = dialog._tr_locale
    for i, name in enumerate(dialog.LAYER_INDEX_MAP):
        dialog._combo_layer_selector.setItemText(
            i, get_string(LAYER_TRANSLATIONS[name], loc)
        )
    for i in range(dialog._combo_theme.count()):
        theme_value = dialog._combo_theme.itemData(i)
        arabic = ARABIC_THEME_NAMES.get(theme_value.lower())
        if arabic:
            dialog._combo_theme.setItemText(i, get_string(arabic, loc))
    for i in range(dialog._combo_action.count()):
        action_key = dialog._combo_action.itemData(i)
        arabic = ARABIC_ACTION_NAMES.get(action_key)
        if arabic:
            dialog._combo_action.setItemText(i, get_string(arabic, loc))
    for i in range(dialog._combo_locale.count()):
        code = dialog._combo_locale.itemData(i)
        if code in LOCALE_LABELS:
            dialog._combo_locale.setItemText(i, LOCALE_LABELS[code][loc])


def init_theme_locale(dialog) -> None:
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    loc = dialog._tr_locale
    dark_arabic = ARABIC_THEME_NAMES['dark']
    light_arabic = ARABIC_THEME_NAMES['light']
    dialog._combo_theme.addItem(get_string(dark_arabic, loc), THEME_DARK)
    dialog._combo_theme.addItem(get_string(light_arabic, loc), THEME_LIGHT)
    saved_theme = settings.value(SETTINGS_KEY_THEME, DEFAULT_THEME)
    theme_map = {
        '\u0641\u0627\u062a\u062d': THEME_LIGHT,
        '\u062f\u0627\u0643\u0646': THEME_DARK,
    }
    saved_theme = theme_map.get(saved_theme, saved_theme)
    try:
        idx = dialog._combo_theme.findData(saved_theme)
    except (ValueError, TypeError):
        idx = -1
    if idx >= 0:
        dialog._combo_theme.setCurrentIndex(idx)
        settings.setValue(SETTINGS_KEY_THEME, saved_theme)
    dialog._current_theme = dialog._combo_theme.currentData()

    for code, _label in AVAILABLE_LOCALES:
        dialog._combo_locale.addItem(LOCALE_LABELS[code][loc], code)
    saved_locale = settings.value(SETTINGS_KEY_LOCALE, '')
    if saved_locale:
        li = dialog._combo_locale.findData(saved_locale)
        if li >= 0:
            dialog._combo_locale.setCurrentIndex(li)


def on_theme_changed(dialog, _index: int) -> None:
    dialog._current_theme = dialog._combo_theme.currentData()
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    settings.setValue(SETTINGS_KEY_THEME, dialog._current_theme)
    dialog.apply_theme()


def on_locale_changed(dialog, _idx: int) -> None:
    code = dialog._combo_locale.currentData()
    if not code:
        return
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    settings.setValue(SETTINGS_KEY_LOCALE, code)
    dialog._tr_locale = code
    clear_i18n_cache()
    apply_widget_texts(dialog, code)
    for b in ('_btn_draw', '_btn_select', '_btn_edit', '_btn_measure'):
        getattr(dialog, b, None) and getattr(dialog, b).setText('')
    translate_internal_combos(dialog)
    fill_wilayas_list(dialog.wilaya_list)
    fill_road_type(dialog._combo_type_road)
    fill_zone_type(dialog._combo_zone_type)
    fill_subdivision_type(dialog._combo_subd_type)
    fill_mounting_status(dialog._combo_mount_status)
    fill_numbering_state(dialog._combo_num_state)
    fill_road_reference(dialog._combo_road_ref)
    fill_panel_reference(dialog._combo_panel_ref)
    fill_feature_combo(dialog.feature_combo)
    fill_paper(dialog._combo_paper)
    fill_org_category(dialog._combo_org_cat)
    fill_activity_category(dialog._combo_activity_cat)
    dialog._update_action_button_texts(dialog._combo_layer_selector.currentIndex())
    if code == 'ar':
        QApplication.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    else:
        QApplication.setLayoutDirection(Qt.LayoutDirection.LeftToRight)


def on_action_changed(dialog, _index: int) -> None:
    action = dialog._combo_action.currentData()
    is_map = action in ('panels_map', 'num_map')
    dialog._combo_paper.setVisible(is_map)
    if action == 'panels_map':
        dialog.panel_chart()
    elif action == 'num_map':
        dialog.numbering_chart()


def on_save_action(dialog) -> None:
    directory = QFileDialog.getExistingDirectory(
        dialog,
        dialog._tr('Choose output directory'),
        dialog._output_dir,
    )
    if not directory:
        return
    dialog._output_dir = directory
    action = dialog._combo_action.currentData()
    if action == 'report':
        dialog.generate_report()
    elif action == 'order':
        dialog.purchase_order()
    elif action == 'panels_map':
        dialog.panel_chart()
        dialog.export_to_image()
    elif action == 'num_map':
        dialog.numbering_chart()
        dialog.export_to_image()
    elif action == 'backup':
        dialog.backup()


def apply_theme(dialog) -> None:
    qss = get_theme_qss(dialog._current_theme)
    dialog.setStyleSheet(qss)
