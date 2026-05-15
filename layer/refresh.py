"""Layer refresh and categorized style management."""
import logging
import os

from sqlalchemy import func
from geoalchemy2 import Geometry

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject, QgsField, QgsFeature, QgsGeometry,
    QgsSymbol, QgsExpression, QgsExpressionContext,
    QgsCategorizedSymbolRenderer, QgsSingleSymbolRenderer, QgsRendererCategory,
)

from ..db.operations import qgis_config
from .. import models as _models
from ..models import get_session
from ..constants import DEFAULT_STYLE_DIR, STYLE_QML

logger = logging.getLogger(__name__)


def refresh_layer_from_db(iface, layer_name, model_name) -> None:
    """Refresh a map layer with data from the database model."""
    session = get_session()
    try:
        model_class = getattr(_models, model_name, None)
        if model_class is None:
            logger.warning("Unknown model: %s", model_name)
            return

        geometry_col = None
        for col in model_class.__table__.columns:
            if isinstance(col.type, Geometry):
                geometry_col = col
                break

        if geometry_col is not None:
            rows = session.query(
                model_class,
                func.ST_AsText(geometry_col).label('geom_wkt'),
            ).all()
            results = [(row[0], row[1]) for row in rows]
        else:
            rows = session.query(model_class).all()
            results = [(row, None) for row in rows]

        if not results:
            return

        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            return
        layer = layers[0]
        provider = layer.dataProvider()

        layer.startEditing()
        ids = [feature.id() for feature in layer.getFeatures()]
        provider.deleteFeatures(ids)
        layer.commitChanges()
        layer.triggerRepaint()

        db_fields = [
            col.name for col in model_class.__table__.columns
            if not isinstance(col.type, Geometry)
        ]
        properties = [
            attr for attr in dir(model_class)
            if isinstance(getattr(model_class, attr), property)
        ]

        all_fields = db_fields + properties

        existing_fields = [field.name() for field in layer.fields()]
        new_fields = []
        for name in all_fields:
            if name not in existing_fields:
                new_fields.append(QgsField(name, QVariant.String))

        if new_fields:
            provider.addAttributes(new_fields)
            layer.updateFields()

        field_names = [field.name() for field in layer.fields()]

        layer.startEditing()

        for result, geom_wkt in results:
            if geom_wkt:
                geom = QgsGeometry.fromWkt(str(geom_wkt))
                feature = QgsFeature()
                feature.setGeometry(geom)

                attributes = []
                for name in field_names:
                    if name in db_fields or name in properties:
                        try:
                            value = getattr(result, name)
                        except Exception:
                            logger.debug(
                                "Attribute %s not found on model instance",
                                name, exc_info=True
                            )
                            value = None
                    else:
                        value = None
                    attributes.append(value)

                feature.setAttributes(attributes)
                provider.addFeature(feature)

        layer.commitChanges()
        layer.triggerRepaint()
    finally:
        session.close()


def apply_categorized_style(iface, layer_name, by) -> None:
    """Apply a categorized renderer to a layer based on field values."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        return
    layer = layers[0]
    expression_string = " || '  ' || ".join(by)
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


def remove_categorized_style(iface, layer_name) -> None:
    """Remove categorized style and revert to single symbol."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        return
    layer = layers[0]
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer = QgsSingleSymbolRenderer(symbol)
    layer.setRenderer(renderer)


def add_feature_to_layer(layer, model_instance, geometry_wkt=None) -> None:
    """Insert a single model instance as a new feature into a QGIS layer.

    This is the fast path — avoids deleting and re-adding all features
    when only one new record needs to appear on the map.
    """
    if geometry_wkt is None:
        geometry = model_instance.geometry
        if geometry is None:
            return
        session = get_session()
        try:
            row = session.query(func.ST_AsText(geometry)).first()
            if row is None:
                return
            geometry_wkt = str(row[0])
        finally:
            session.close()

    geom = QgsGeometry.fromWkt(geometry_wkt)
    provider = layer.dataProvider()

    model_class = type(model_instance)
    db_fields = [
        col.name for col in model_class.__table__.columns
        if not isinstance(col.type, Geometry)
    ]
    properties = [
        attr for attr in dir(model_class)
        if isinstance(getattr(model_class, attr), property)
    ]
    all_fields = db_fields + properties
    field_names = [field.name() for field in layer.fields()]

    feature = QgsFeature()
    feature.setGeometry(geom)

    attributes = []
    for name in field_names:
        if name in all_fields:
            try:
                value = getattr(model_instance, name)
            except Exception:
                value = None
        else:
            value = None
        attributes.append(value)
    feature.setAttributes(attributes)

    was_editing = layer.isEditable()
    if not was_editing:
        layer.startEditing()
    provider.addFeature(feature)
    layer.commitChanges()
    layer.triggerRepaint()


def refresh_all_layers(iface) -> None:
    """Refresh all mapper layers and apply stored styles."""
    data_list = qgis_config().get('mapper')
    for data in data_list:
        try:
            refresh_layer_from_db(iface, data.get("layer"), data.get("model"))
        except Exception as e:
            logger.error("Error occurred: %s", e)

    data_list = qgis_config().get('other_layers')
    for dl in data_list:
        layers = QgsProject.instance().mapLayersByName(dl.get('label'))
        if layers:
            filename = os.path.join(DEFAULT_STYLE_DIR, dl.get('style'))
            layers[0].loadNamedStyle(filename)


def apply_all_categorized_styles(iface) -> None:
    """Apply categorized styles to all configured layers."""
    data_list = qgis_config().get('categorize')
    for data in data_list:
        try:
            apply_categorized_style(iface, data.get("layer"), data.get("by"))
        except Exception as e:
            logger.error("Error occurred: %s", e)


def remove_all_categorized_styles(iface) -> None:
    """Remove categorized styles from all configured layers."""
    data_list = qgis_config().get('other_layers')
    for data in data_list:
        try:
            remove_categorized_style(iface, data.get("label"))
        except Exception as e:
            logger.error("Error occurred: %s", e)

    filename = STYLE_QML
    for layer in QgsProject.instance().mapLayers().values():
        layer.loadNamedStyle(filename)
