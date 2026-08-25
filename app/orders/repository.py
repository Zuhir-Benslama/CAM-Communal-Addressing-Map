"""Repository layer for CRUD operations on spatial entities."""

from typing import Any

from geoalchemy2.elements import WKTElement
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..core.database import get_session
from ..orders.models import (
    Numbering,
    Organization,
    PanelSign,
    Road,
    Subdivision,
    Zone,
)
from ..shared.constants import DEFAULT_PANEL_DIM, PANEL_TYPE_MAP, SRID


def _add_entity(instance: Any, session: Session | None = None) -> Any:
    """Save a model instance with automatic session management."""
    own_session = session is None
    _session: Session = get_session() if own_session else session
    try:
        instance.save(_session)
        return instance
    finally:
        if own_session:
            _session.close()


def add_panel_sign(
    *,
    geometry_wkt: str,
    mount_status: str,
    road_id: str | None = None,
    subdivision_id: str | None = None,
    organization_id: str | None = None,
    dimensions: str | None = None,
    record_id: str | None = None,
) -> PanelSign:
    """Create and persist a new PanelSign entity."""
    instance = PanelSign(
        id=record_id,
        status=mount_status,
        road_id=road_id,
        subdivision_id=subdivision_id,
        organization_id=organization_id,
        dimensions=dimensions or DEFAULT_PANEL_DIM,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def add_organization(
    *,
    geometry_wkt: str,
    org_name: str,
    org_type: str,
    org_cat: str,
    record_id: str | None = None,
    name_fr: str | None = None,
    name_en: str | None = None,
) -> Organization:
    """Create and persist a new Organization entity."""
    instance = Organization(
        id=record_id,
        type=org_type,
        category=org_cat,
        name=org_name,
        name_fr=name_fr,
        name_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def add_road(
    *,
    geometry_wkt: str,
    road_name: str,
    type_road: str,
    road_decision: str,
    record_id: str | None = None,
    name_fr: str | None = None,
    name_en: str | None = None,
) -> Road:
    """Create and persist a new Road entity."""
    instance = Road(
        id=record_id,
        type=type_road,
        name=road_name,
        decision_number=road_decision,
        name_fr=name_fr,
        name_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def add_numbering(
    *,
    geometry_wkt: str,
    value: str,
    road_id: str | None = None,
    subdivision_id: str | None = None,
    repetition: str | None = None,
    state: str | None = None,
    activity_cat: str | None = None,
    activity_type: str | None = None,
    record_id: str | None = None,
) -> Numbering:
    """Create and persist a new Numbering entity."""
    instance = Numbering(
        id=record_id,
        value=value,
        road_id=road_id,
        subdivision_id=subdivision_id,
        repetition=repetition,
        state=state,
        activity_cat=activity_cat,
        activity_type=activity_type,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def add_subdivision(
    *,
    geometry_wkt: str,
    subdivision_type: str,
    name: str,
    record_id: str | None = None,
    name_fr: str | None = None,
    name_en: str | None = None,
) -> Subdivision:
    """Create and persist a new Subdivision entity."""
    instance = Subdivision(
        id=record_id,
        name=name,
        type=subdivision_type,
        name_fr=name_fr,
        name_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def add_zone(
    *,
    geometry_wkt: str,
    zone_type: str,
    name: str,
    record_id: str | None = None,
    name_fr: str | None = None,
    name_en: str | None = None,
) -> Zone:
    """Create and persist a new Zone entity."""
    instance = Zone(
        id=record_id,
        name=name,
        type=zone_type,
        name_fr=name_fr,
        name_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    return _add_entity(instance)


def count_numberings(state: str) -> int:
    """Count numberings by state (query Num view in Views.sql)."""
    session = get_session()
    try:
        result = session.execute(
            text('select count(*) as cpt from Num where state = :state'),
            {'state': state},
        )
        row = result.fetchone()
        return row[0] if row else 0
    finally:
        session.close()


def count_panels(panel_type: str, state: str) -> int:
    """Count panels by type and state (query Pan view in Views.sql)."""
    db_type = PANEL_TYPE_MAP.get(panel_type, panel_type)
    session = get_session()
    try:
        result = session.execute(
            text(
                'select count(*) as cpt from Pan where type = :type and status = :state'
            ),
            {'type': db_type, 'state': state},
        )
        row = result.fetchone()
        return row[0] if row else 0
    finally:
        session.close()


def query_missing_pan(state: str) -> list:
    """Query missing panels grouped by label/type
    from the Pan2 view (defined in Views.sql)."""
    session = get_session()
    try:
        result = session.execute(
            text(
                'SELECT label, type, COUNT(*) AS total '
                'FROM Pan2 WHERE status = :state GROUP BY label, type'
            ),
            {'state': state},
        )
        rows = result.fetchall()
        return [{'label': row[0], 'type': row[1], 'total': row[2]} for row in rows]
    finally:
        session.close()


def query_missing_num(state: str) -> list:
    """Query numberings without repetition grouped by value from Num view."""
    session = get_session()
    try:
        result = session.execute(
            text(
                'SELECT value, COUNT(*) AS total FROM Num '
                'WHERE state = :state '
                "AND (repetition = '' OR repetition IS NULL) GROUP BY value"
            ),
            {'state': state},
        )
        rows = result.fetchall()
        return [{'value': row[0], 'total': row[1]} for row in rows]
    finally:
        session.close()


def query_missing_rep(state: str) -> list:
    """Query numberings WITH repetition grouped by value from Num view."""
    session = get_session()
    try:
        result = session.execute(
            text(
                'SELECT repetition, COUNT(*) AS total FROM Num '
                'WHERE state = :state '
                "AND (repetition != '' OR repetition IS NOT NULL) "
                'GROUP BY repetition'
            ),
            {'state': state},
        )
        rows = result.fetchall()
        return [{'value': row[0], 'total': row[1]} for row in rows]
    finally:
        session.close()
