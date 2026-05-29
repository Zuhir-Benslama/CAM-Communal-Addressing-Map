"""Layer creation and initialization utilities."""
import json
import logging

import toml
from sqlalchemy import Integer, SmallInteger, Float, String, Text, Boolean, func
from geoalchemy2 import Geometry

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsField, QgsFeature,
    QgsGeometry, QgsFillSymbol,
)

from ..app.orders import models as _models
from ..app.users.repository import qgis_config, get_current_user
from ..app.core.database import get_session
from ..app.users.models import User
from ..constants import CRS, COOKIE_FILE, LAYER_MUNICIPALITY, MEMORY_PROVIDER, LOCALITE_GEOJSON

logger = logging.getLogger(__name__)


def create_other_layers(_iface) -> None:
    """Create non-mapper vector layers from QGIS config."""
    other_layer_list = qgis_config().get('other_layers') or []
    mapper = qgis_config().get('mapper') or []
    for layer_cfg in other_layer_list:
        layer = QgsVectorLayer(
            layer_cfg.get('url'), layer_cfg.get('label'), MEMORY_PROVIDER
        )
        if layer.isValid():
            existing = QgsProject.instance().mapLayersByName(layer_cfg.get('label'))
            if not existing:
                QgsProject.instance().addMapLayer(layer)
                model_name = None
                for cfg in mapper:
                    if cfg.get("layer") == layer.name():
                        model_name = cfg.get("model")
                        break

                model_class = getattr(_models, model_name, None) if model_name else None
                if model_class is None:
                    continue
                fields = []
                for column_name, column_obj in \
                        model_class.__table__.columns.items():
                    if isinstance(column_obj.type, Geometry):
                        continue

                    column_type = column_obj.type

                    if isinstance(column_type, (Integer, SmallInteger)):
                        field_type = QVariant.Int
                    elif isinstance(column_type, Float):
                        field_type = QVariant.Double
                    elif isinstance(column_type, String):
                        field_type = QVariant.String
                    elif isinstance(column_type, Text):
                        field_type = QVariant.String
                    elif isinstance(column_type, Boolean):
                        field_type = QVariant.Bool
                    else:
                        field_type = QVariant.String

                    fields.append(QgsField(column_name, field_type))

                layer.startEditing()
                provider = layer.dataProvider()
                provider.addAttributes(fields)
                layer.updateFields()
                layer.commitChanges()
                layer.triggerRepaint()


def init_allowed_zone(iface) -> None:
    """Create the municipality boundary layer from the authenticated user."""
    user_data = get_current_user()
    commune_code = user_data.get('commune_code') if user_data else None

    wkt = None
    if commune_code:
        try:
            with open(LOCALITE_GEOJSON, 'r', encoding='utf-8') as f:
                fc = json.load(f)
            for feature in fc.get('features', []):
                if feature.get('properties', {}).get('commune_code') == commune_code:
                    geom = feature.get('geometry')
                    if geom:
                        wkt = _geojson_to_wkt(geom.get('type', ''), geom.get('coordinates', []))
                    break
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("Could not load %s", LOCALITE_GEOJSON)

    if wkt:
        multipolygon = QgsGeometry.fromWkt(wkt)
    else:
        multipolygon = QgsGeometry()

    existing_layer = (
        QgsProject.instance()
        .mapLayersByName(LAYER_MUNICIPALITY)
    )

    if not existing_layer:
        layer = QgsVectorLayer(
            f'MultiPolygon?crs={CRS}',
            LAYER_MUNICIPALITY,
            MEMORY_PROVIDER
        )
        layer.setMinimumScale(10000000)
        provider = layer.dataProvider()
        layer.updateFields()

        if multipolygon and not multipolygon.isEmpty():
            feature = QgsFeature()
            feature.setGeometry(multipolygon)
            feature.setAttributes([1])
            provider.addFeature(feature)
            layer.updateExtents()

            symbol = QgsFillSymbol.createSimple({
                'color': 'transparent',
                'outline_color': 'red',
                'outline_width': '0.5'
            })

            layer.renderer().setSymbol(symbol)
            QgsProject.instance().addMapLayer(layer)

        if multipolygon and not multipolygon.isEmpty():
            iface.mapCanvas().zoomToFeatureExtent(
                multipolygon.boundingBox()
            )
        iface.mapCanvas().refresh()

    create_other_layers(iface)


def _geojson_to_wkt(geom_type: str, coords: list) -> str:
    """Convert a GeoJSON geometry to WKT string."""
    if geom_type == 'MultiPolygon':
        parts = []
        for polygon in coords:
            rings = []
            for ring in polygon:
                pts = ', '.join(f'{p[0]} {p[1]}' for p in ring)
                rings.append(f'({pts})')
            parts.append('(' + ', '.join(rings) + ')')
        return f'MULTIPOLYGON ({", ".join(parts)})'
    elif geom_type == 'Polygon':
        rings = []
        for ring in coords:
            pts = ', '.join(f'{p[0]} {p[1]}' for p in ring)
            rings.append(f'({pts})')
        return f'POLYGON ({", ".join(rings)})'
    elif geom_type == 'MultiLineString':
        parts = []
        for line in coords:
            pts = ', '.join(f'{p[0]} {p[1]}' for p in line)
            parts.append(f'({pts})')
        return f'MULTILINESTRING ({", ".join(parts)})'
    elif geom_type == 'LineString':
        pts = ', '.join(f'{p[0]} {p[1]}' for p in coords)
        return f'LINESTRING ({pts})'
    elif geom_type == 'MultiPoint':
        pts = ', '.join(f'{p[0]} {p[1]}' for p in coords)
        return f'MULTIPOINT ({pts})'
    elif geom_type == 'Point':
        return f'POINT ({coords[0]} {coords[1]})'
    return ''
