"""Proxy classes that mimic PyQt widgets for QML-backed dialog access.

Each proxy implements a subset of the real PyQt widget API so that
existing fill_* and handler functions work unchanged with QML.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .main_dialog import MainDialogBridge

# ---------------------------------------------------------------------------
# Combo proxy
# ---------------------------------------------------------------------------


class _ComboProxy:
    """Proxy that mimics a QComboBox for QML-backed combo access.

    Methods match PyQt QComboBox naming so fill_* functions work unchanged.
    """

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []
        self._blocked = False
        self._index = -1

    def clear(self) -> None:
        self._items = []
        self._index = -1

    def addItem(self, text: str, value: Any = None) -> None:
        was_empty = len(self._items) == 0
        self._items.append({'text': str(text), 'value': value})
        if was_empty and self._index < 0:
            self._index = 0

    def count(self) -> int:
        return len(self._items)

    def currentIndex(self) -> int:
        return self._index

    def setCurrentIndex(self, index: int) -> None:
        self._index = index

    def currentText(self) -> str:
        if 0 <= self._index < len(self._items):
            return str(self._items[self._index].get('text', ''))
        return ''

    def currentData(self) -> Any:
        if 0 <= self._index < len(self._items):
            return self._items[self._index].get('value')
        return None

    def itemData(self, index: int) -> Any:
        if 0 <= index < len(self._items):
            return self._items[index].get('value')
        return None

    def itemText(self, index: int) -> str:
        if 0 <= index < len(self._items):
            return str(self._items[index].get('text', ''))
        return ''

    def setItemText(self, index: int, text: str) -> None:
        if 0 <= index < len(self._items):
            self._items[index]['text'] = str(text)

    def findData(self, value: Any) -> int:
        for i, item in enumerate(self._items):
            if item.get('value') == value:
                return i
        return -1

    def blockSignals(self, blocked: bool) -> bool:
        old = self._blocked
        self._blocked = blocked
        return old

    def setVisible(self, visible: bool) -> None:
        pass

    def completer(self) -> None:
        return None

    def setInsertPolicy(self, policy: object) -> None:
        pass


# ---------------------------------------------------------------------------
# Field proxy
# ---------------------------------------------------------------------------


class _FieldProxy:
    """Proxy that mimics a QLineEdit / QLabel for QML access."""

    def __init__(self) -> None:
        self._text = ''

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = str(text)

    def clear(self) -> None:
        self._text = ''

    def setAlignment(self, *args: Any) -> None:
        pass

    def setSizePolicy(self, *args: Any) -> None:
        pass

    def setMinimumWidth(self, *args: Any) -> None:
        pass

    def setMinimumHeight(self, *args: Any) -> None:
        pass

    def setMaximumWidth(self, *args: Any) -> None:
        pass

    def setVisible(self, visible: bool) -> None:
        pass

    def setProperty(self, name: str, value: Any) -> None:
        pass

    def height(self) -> int:
        return 34


# ---------------------------------------------------------------------------
# Router proxy (stacked widget)
# ---------------------------------------------------------------------------


class _RouterProxy:
    """Proxy that mimics a QStackedWidget for router navigation."""

    def __init__(self, bridge: 'MainDialogBridge') -> None:
        self._bridge = bridge

    @staticmethod
    def findChild(cls: type, name: str) -> object:
        from types import SimpleNamespace

        return SimpleNamespace(objectName=lambda: str(name))

    def setCurrentWidget(self, page: object) -> None:
        name = page.objectName() if hasattr(page, 'objectName') else str(page)
        self._bridge._switch_page(str(name))


# ---------------------------------------------------------------------------
# Menu proxy (tab widget)
# ---------------------------------------------------------------------------


class _MenuProxy:
    """Proxy that mimics a QTabWidget for menu tab access."""

    def __init__(self, bridge: 'MainDialogBridge') -> None:
        self._bridge = bridge

    def setCurrentIndex(self, index: int) -> None:
        self._bridge._set_tab_index(index)

    def currentIndex(self) -> int:
        return self._bridge._get_tab_index()

    def currentWidget(self) -> Any:
        idx = self.currentIndex()
        from types import SimpleNamespace

        return SimpleNamespace(
            objectName=lambda: 'tab_ops' if idx == 0 else 'tab',
        )

    def setDocumentMode(self, val: bool) -> None:
        pass

    def setUsesScrollButtons(self, val: bool) -> None:
        pass

    def setStyleSheet(self, ss: str) -> None:
        pass

    def tabText(self, index: int) -> str:
        names = {0: 'Operations', 1: 'Report', 2: 'Settings'}
        return names.get(index, '')

    def tabBar(self) -> object:
        class _TabBar:
            @staticmethod
            def hide() -> None:
                pass

        return _TabBar()


# ---------------------------------------------------------------------------
# Form stack proxy
# ---------------------------------------------------------------------------


class _FormStackProxy:
    """Proxy that mimics a QStackedWidget for form stack access."""

    def __init__(self, bridge: 'MainDialogBridge') -> None:
        self._bridge = bridge

    def setCurrentIndex(self, index: int) -> None:
        self._bridge._set_form_stack_index(index)

    def currentIndex(self) -> int:
        return self._bridge._get_form_stack_index()


# ---------------------------------------------------------------------------
# Widget name registries
# ---------------------------------------------------------------------------

_COMBO_NAMES = frozenset(
    {
        'wilaya_list',
        'commune_of_wilaya',
        'map_options',
        'org_cat',
        'org_type',
        'activity_cat',
        'activity_type',
        'road_ref',
        'panel_ref',
        'paper',
        'mount_status',
        'num_state',
        'subd_type',
        'type_road',
        'zone_type',
        'layer_selector',
        'feature_combo',
        'subtype_combo',
        '_theme_combo',
        '_locale_combo',
        '_action_combo',
    }
)

_FIELD_NAMES = frozenset(
    {
        'username',
        'password',
        'uname',
        'pwd',
        'email',
        'fname',
        'lname',
        'pnum',
        'nom_zone',
        'road_name',
        'org_name',
        'subd_name',
        'num_val',
        'repetition',
        'ref_name',
        'ref_name2',
        'label_username',
        'new_type',
        'label_subtype',
        'lineEdit_type',
        'lineEdit_by',
        'lineEdit_nummokh',
        'dateEdit',
    }
)
