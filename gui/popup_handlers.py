"""Entity-specific form population and update handlers for PopupDialog.

Populate functions return data dicts for form fields.
Update functions read from ``dialog._current_form_data`` dict.
"""

import logging
from typing import TYPE_CHECKING, Any

from qgis.PyQt.QtWidgets import QMessageBox
from sqlalchemy.exc import SQLAlchemyError

from ..app.core.database import get_session
from ..app.orders.models import (
    Numbering,
    Organization,
    PanelSign,
    Road,
    Subdivision,
    Zone,
)
from ..constants import (
    LAYER_FACILITIES,
    LAYER_NUMBERING,
    LAYER_PANELS,
    LAYER_ROADS,
    LAYER_SUBDIVISIONS,
    LAYER_ZONES,
    locale_value,
    validate_text,
)
from ..layer.refresh import refresh_all_layers
from ..scripts.widget_texts import get_string

if TYPE_CHECKING:
    from .popup_dialog import PopupDialog

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Populate helpers (read from DB → return data dict for form)
# ---------------------------------------------------------------------------


def _populate_name_type(query: Any, loc: str) -> dict:
    """Return a dict with locale-aware name and type fields."""
    return {
        'name': locale_value(query, 'name', loc),
        'type': query.type,
    }


def populate_road(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    return _populate_name_type(query, loc)


def populate_facility(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    return {
        **_populate_name_type(query, loc),
        'category': query.category,
    }


def populate_subdivision(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    return _populate_name_type(query, loc)


def populate_zone(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    return _populate_name_type(query, loc)


def populate_numbering(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    data: dict = {
        'number': query.value or '',
        'repetition': query.repetition or '',
        'state': query.state or '',
    }
    if query.road_id:
        data['refType'] = LAYER_ROADS
        data['refName'] = (
            locale_value(query.road, 'type', loc)
            + ' '
            + locale_value(query.road, 'name', loc)
        )
    elif query.subdivision_id:
        data['refType'] = LAYER_SUBDIVISIONS
        data['refName'] = locale_value(query.subdivision, 'name', loc)
    data['activityCat'] = query.activity_cat or ''
    data['activityType'] = query.activity_type or ''
    return data


def populate_panel(_dialog: 'PopupDialog', query: Any, loc: str) -> dict:
    data: dict = {
        'mountStatus': query.status or '',
    }
    if query.road_id:
        data['refType'] = LAYER_ROADS
        data['refName'] = (
            locale_value(query.road, 'type', loc)
            + ' '
            + locale_value(query.road, 'name', loc)
        )
    elif query.organization_id:
        data['refType'] = LAYER_FACILITIES
        data['refName'] = (
            locale_value(query.organization, 'type', loc)
            + ' '
            + locale_value(query.organization, 'name', loc)
        )
    elif query.subdivision_id:
        data['refType'] = LAYER_SUBDIVISIONS
        data['refName'] = locale_value(query.subdivision, 'name', loc)
    return data


POPULATE_DISPATCH = {
    LAYER_ROADS: populate_road,
    LAYER_FACILITIES: populate_facility,
    LAYER_SUBDIVISIONS: populate_subdivision,
    LAYER_ZONES: populate_zone,
    LAYER_NUMBERING: populate_numbering,
    LAYER_PANELS: populate_panel,
}


# ---------------------------------------------------------------------------
# Update helpers (read dialog._current_form_data → write DB → notify)
# ---------------------------------------------------------------------------


def _notify_success(dialog: 'PopupDialog', msg_key: str) -> None:
    QMessageBox.information(
        dialog,
        get_string('Success', dialog._tr_locale),
        get_string(msg_key, dialog._tr_locale),
    )


def _notify_failure(dialog: 'PopupDialog', msg_key: str, exc: Exception) -> None:
    logger.exception('Failed to update: %s', exc)
    QMessageBox.critical(
        dialog,
        get_string('Error', dialog._tr_locale),
        get_string(msg_key, dialog._tr_locale),
    )


def _finish_update(dialog: 'PopupDialog') -> None:
    refresh_all_layers(dialog.iface)
    dialog.close()


def _data(dialog: 'PopupDialog') -> dict:
    return dialog._current_form_data


def _update_entity(
    dialog: 'PopupDialog',
    model_class: type[Any],
    success_msg: str,
    error_msg: str,
    **fields: Any,
) -> None:
    """Generic update helper: open session, call model.update, notify."""
    session = get_session()
    try:
        model_class.update(session, record_id=dialog.attribute, **fields)
        _notify_success(dialog, success_msg)
    except (ValueError, SQLAlchemyError) as e:
        _notify_failure(dialog, error_msg, e)
    finally:
        session.close()
    _finish_update(dialog)


def update_road(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    _update_entity(
        dialog,
        Road,
        'This road has been updated successfully',
        'Cannot update road',
        name=validate_text(data.get('name', '')),
        type=data.get('type', ''),
    )


def update_organization(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    _update_entity(
        dialog,
        Organization,
        'This facility has been updated successfully',
        'Cannot update facility',
        category=data.get('category', ''),
        name=validate_text(data.get('name', '')),
        type=data.get('type', ''),
    )


def update_subdivision(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    _update_entity(
        dialog,
        Subdivision,
        'This subdivision has been updated successfully',
        'Cannot update subdivision',
        name=validate_text(data.get('name', '')),
        type=data.get('type', ''),
    )


def update_zone(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    _update_entity(
        dialog,
        Zone,
        'This zone has been updated successfully',
        'Cannot update zone',
        name=validate_text(data.get('name', '')),
        type=data.get('type', ''),
    )


def update_panel(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    session = get_session()
    try:
        ref_id = dialog._ref_id or None
        ref_layer = dialog._ref_layer or ''

        kwargs = {
            'status': data.get('mountStatus', ''),
        }

        if ref_id:
            if ref_layer == LAYER_FACILITIES:
                kwargs['organization_id'] = ref_id
                kwargs['road_id'] = None
                kwargs['subdivision_id'] = None
            elif ref_layer == LAYER_ROADS:
                kwargs['road_id'] = ref_id
                kwargs['subdivision_id'] = None
                kwargs['organization_id'] = None
            elif ref_layer == LAYER_SUBDIVISIONS:
                kwargs['subdivision_id'] = ref_id
                kwargs['road_id'] = None
                kwargs['organization_id'] = None

        PanelSign.update(
            session,
            record_id=dialog.attribute,
            **kwargs,
        )
        _notify_success(dialog, 'This panel has been updated successfully')
    except (ValueError, SQLAlchemyError) as e:
        _notify_failure(dialog, 'Cannot update panel', e)
    finally:
        session.close()
    _finish_update(dialog)


def update_numbering(dialog: 'PopupDialog') -> None:
    data = _data(dialog)
    session = get_session()
    try:
        ref_id = dialog._ref_id or None
        ref_layer = dialog._ref_layer or ''

        kwargs: dict = {
            'repetition': validate_text(data.get('repetition', '')),
            'value': validate_text(data.get('number', '')),
            'state': data.get('state', ''),
            'road_id': None,
            'subdivision_id': None,
            'organization_id': None,
            'activity_cat': data.get('activityCat', ''),
            'activity_type': data.get('activityType', ''),
        }

        if ref_id:
            if ref_layer == LAYER_FACILITIES:
                kwargs['organization_id'] = ref_id
            elif ref_layer == LAYER_ROADS:
                kwargs['road_id'] = ref_id
            elif ref_layer == LAYER_SUBDIVISIONS:
                kwargs['subdivision_id'] = ref_id

        Numbering.update(session, record_id=dialog.attribute, **kwargs)

        _notify_success(dialog, 'This numbering has been updated successfully')
    except (ValueError, SQLAlchemyError) as e:
        _notify_failure(dialog, 'Cannot update numbering', e)
    finally:
        session.close()
    _finish_update(dialog)
