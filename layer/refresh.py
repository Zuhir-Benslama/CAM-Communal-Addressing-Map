"""Layer refresh and categorized style management."""

import logging
import os
from typing import Any

from geoalchemy2 import Geometry
from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsExpression,
    QgsExpressionContext,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsProject,
    QgsRendererCategory,
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsVectorLayer,
)

try:
    from qgis.core import QVariant
except ImportError:
    from enum import IntEnum

    class QVariant(IntEnum):  # type: ignore[no-redef]
        Bool = 1
        Int = 2
        Double = 6
        String = 10


from sqlalchemy import func

from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import DEFAULT_STYLE_DIR, STYLE_QML

logger = logging.getLogger(__name__)


def _get_model_class(model_name: str):
    """Look up a model class by name, returning None if not found."""
    model_class = getattr(_models, model_name, None)
    if model_class is None:
        logger.warning('Unknown model: %s', model_name)
    return model_class


def _get_geometry_column(model_class) -> Any | None:
    """Find the geometry column on a model, or None."""
    for col in model_class.__table__.columns:
        if isinstance(col.type, Geometry):
            return col
    return None


def _get_all_model_fields(model_class) -> list[str]:
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
    session,
    model_class,
    geometry_col,
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


def _build_feature(result, geom_wkt, field_names, all_fields) -> QgsFeature | None:
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


def _commit_feature(layer, feature) -> None:
    """Add a feature to a layer within an edit session."""
    provider = layer.dataProvider()
    was_editing = layer.isEditable()
    if not was_editing:
        layer.startEditing()
    provider.addFeature(feature)
    layer.commitChanges()
    layer.triggerRepaint()


def refresh_layer_from_db(_iface, layer_name, model_name) -> None:
    """Refresh a map layer with data from the database model."""
    session = get_session()
    try:
        model_class = _get_model_class(model_name)
        if model_class is None:
            return

        geometry_col = _get_geometry_column(model_class)
        results = _query_all_records(session, model_class, geometry_col)
        if not results:
            return

        layer = _get_layer(layer_name)
        if layer is None:
            return
        provider = layer.dataProvider()

        all_fields = _get_all_model_fields(model_class)
        new_fields = _get_new_layer_fields(layer, all_fields)
        field_names = [field.name() for field in layer.fields()]

        layer.startEditing()

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

        layer.commitChanges()
        layer.triggerRepaint()
    finally:
        session.close()


def apply_categorized_style(_iface, layer_name, category_fields) -> None:
    """Apply a categorized renderer to a layer based on field values."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        return
    layer = layers[0]
    expression_string = " || '  ' || ".join(category_fields)
    expression = QgsExpression(expression_string)
    unique_values = set()
    for feature in layer.getFeatures():
        context = QgsExpressionContext()
        context.setFeature(feature)
        result = expression.evaluate(context)
        unique_values.add(result)
    categories = []

    for value in unique_values:
        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        category = QgsRendererCategory(value, symbol, str(value))
        categories.append(category)

    renderer = QgsCategorizedSymbolRenderer(expression_string, categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()


def remove_categorized_style(_iface, layer_name) -> None:
    """Remove categorized style and revert to single symbol."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        return
    layer = layers[0]
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)


def _resolve_wkt(model_instance, geometry=None) -> str | None:
    """Resolve geometry WKT from model geometry attribute or explicit value."""
    if geometry is not None:
        return geometry
    geom = model_instance.geometry
    if geom is None:
        return None
    session = get_session()
    try:
        row = session.query(func.ST_AsText(geom)).first()
        return str(row[0]) if row else None
    finally:
        session.close()


def add_feature_to_layer(layer, model_instance, geometry_wkt=None) -> None:
    """Insert a single model instance as a new feature into a QGIS layer.

    This is the fast path — avoids deleting and re-adding all features
    when only one new record needs to appear on the map.
    """
    wkt = _resolve_wkt(model_instance, geometry_wkt)
    if wkt is None:
        return

    all_fields = _get_all_model_fields(type(model_instance))
    field_names = [field.name() for field in layer.fields()]
    feature = _build_feature(model_instance, wkt, field_names, all_fields)
    if feature:
        _commit_feature(layer, feature)


def refresh_all_layers(iface) -> None:
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
            filename = os.path.join(DEFAULT_STYLE_DIR, layer_cfg.get('style'))
            result = layers[0].loadNamedStyle(filename)
            logger.info(
                "loadNamedStyle('%s') for '%s': %s",
                filename,
                layer_cfg.get('label'),
                result,
            )


def apply_all_categorized_styles(iface) -> None:
    """Apply categorized styles to all configured layers."""
    data_list = qgis_config().get('categorize') or []
    for cfg in data_list:
        try:
            apply_categorized_style(iface, cfg.get('layer'), cfg.get('by'))
        except Exception:  # pylint: disable=W0718
            logger.exception('Error applying categorized style to %s', cfg.get('layer'))


def remove_all_categorized_styles(iface) -> None:
    """Remove categorized styles from all configured layers."""
    data_list = qgis_config().get('other_layers') or []
    for cfg in data_list:
        try:
            remove_categorized_style(iface, cfg.get('label'))
        except Exception:  # pylint: disable=W0718
            logger.exception('Error removing categorized style from %s', cfg.get('label'))

    filename = STYLE_QML
    for layer in QgsProject.instance().mapLayers().values():
        layer.loadNamedStyle(filename)
