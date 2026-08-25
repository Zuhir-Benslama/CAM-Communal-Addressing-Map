"""Layer refresh utilities."""

import datetime
import logging
from typing import Any

from geoalchemy2 import Geometry
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer,
)
from sqlalchemy import func

from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import DEFAULT_STYLE_DIR
from .utils import QVariant

logger = logging.getLogger(__name__)


def _get_model_class(model_name: str) -> Any | None:
    """Look up a model class by name, returning None if not found."""
    model_class = getattr(_models, model_name, None)
    if model_class is None:
        logger.warning('Unknown model: %s', model_name)
    return model_class


def _get_geometry_column(model_class: Any) -> Any | None:
    """Find the geometry column on a model, or None."""
    for col in model_class.__table__.columns:
        if isinstance(col.type, Geometry):
            return col
    return None


def _get_all_model_fields(model_class: Any) -> list[str]:
    """Return list of non-geometry DB columns plus Python properties."""
    db_fields = [
        col.name
        for col in model_class.__table__.columns
        if not isinstance(col.type, Geometry)
    ]
    properties = [
        attr
        for attr in dir(model_class)
        if isinstance(getattr(model_class, attr), property)
    ]
    return db_fields + properties


def _get_layer(layer_name: str) -> QgsVectorLayer | None:
    """Return the first map layer matching name, or None."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    return layers[0] if layers else None


def _get_new_layer_fields(
    layer: QgsVectorLayer,
    all_fields: list[str],
) -> list[QgsField]:
    """Return QgsField objects for any fields not yet on the layer."""
    existing = {field.name() for field in layer.fields()}
    return [
        QgsField(name, QVariant.String) for name in all_fields if name not in existing
    ]


def _query_all_records(
    session: Any,
    model_class: Any,
    geometry_col: Any,
) -> list[tuple[Any, str | None]]:
    """Query all model records, eagerly loading geometry WKT if available."""
    if geometry_col is not None:
        rows = session.query(
            model_class,
            func.ST_AsText(geometry_col).label('geom_wkt'),
        ).all()
        return [(row[0], row[1]) for row in rows]
    rows = session.query(model_class).all()
    return [(row, None) for row in rows]


def _build_feature(
    result: Any, geom_wkt: Any, field_names: list[str], all_fields: list[str]
) -> QgsFeature | None:
    """Build a QgsFeature from a model instance and geometry WKT."""
    if not geom_wkt:
        return None
    geom = QgsGeometry.fromWkt(str(geom_wkt))
    feature = QgsFeature()
    feature.setGeometry(geom)
    attributes = []
    for name in field_names:
        if name in all_fields:
            try:
                value = getattr(result, name)
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
            except AttributeError:
                logger.debug(
                    'Attribute %s not found on model instance', name, exc_info=True
                )
                value = None
        else:
            value = None
        attributes.append(value)
    feature.setAttributes(attributes)
    return feature


def refresh_layer_from_db(_iface: Any, layer_name: str, model_name: str) -> None:
    """Refresh a map layer with data from the database model."""
    session = get_session()
    try:
        model_class = _get_model_class(model_name)
        if model_class is None:
            return

        geometry_col = _get_geometry_column(model_class)
        results = _query_all_records(session, model_class, geometry_col)

        layer = _get_layer(layer_name)
        if layer is None:
            return
        provider = layer.dataProvider()

        all_fields = _get_all_model_fields(model_class)
        new_fields = _get_new_layer_fields(layer, all_fields)
        field_names = [field.name() for field in layer.fields()]

        layer.startEditing()
        try:
            ids = [feature.id() for feature in layer.getFeatures()]
            provider.deleteFeatures(ids)

            if new_fields:
                provider.addAttributes(new_fields)
                layer.updateFields()
                field_names = [f.name() for f in layer.fields()]

            for result, geom_wkt in results:
                feature = _build_feature(result, geom_wkt, field_names, all_fields)
                if feature:
                    provider.addFeature(feature)
        except Exception:
            layer.rollBack()
            raise

        if not layer.commitChanges():
            logger.error('Commit failed for %s: %s', layer_name, layer.commitErrors())
            layer.rollBack()
        else:
            layer.triggerRepaint()
    finally:
        session.close()


def refresh_all_layers(iface: Any) -> None:
    """Refresh all mapper layers and apply stored styles."""
    data_list = qgis_config().get('mapper') or []
    for cfg in data_list:
        try:
            refresh_layer_from_db(iface, cfg.get('layer'), cfg.get('model'))
        except Exception:  # pylint: disable=W0718
            logger.exception('Error refreshing layer %s', cfg.get('layer'))

    data_list = qgis_config().get('other_layers') or []
    for layer_cfg in data_list:
        layers = QgsProject.instance().mapLayersByName(layer_cfg.get('label'))
        if layers:
            filename = DEFAULT_STYLE_DIR / layer_cfg.get('style')
            result = layers[0].loadNamedStyle(str(filename))
            logger.info(
                "loadNamedStyle('%s') for '%s': %s",
                filename,
                layer_cfg.get('label'),
                result,
            )
