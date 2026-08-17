"""Layer creation and initialization utilities."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from geoalchemy2 import Geometry
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsProject,
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


from sqlalchemy import Boolean, Float, Integer, SmallInteger, String, Text

from ..app.orders import models as _models
from ..app.users.repository import get_current_user, qgis_config
from ..constants import (
    COMMUNES_DB,
    COMMUNES_JSON,
    CRS,
    LAYER_MUNICIPALITY,
    MEMORY_PROVIDER,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQLAlchemy → QVariant type mapping
# ---------------------------------------------------------------------------

_TYPE_MAP: list[tuple[tuple, object]] = [
    ((Integer, SmallInteger), QVariant.Int),
    ((Float,), QVariant.Double),
    ((String, Text), QVariant.String),
    ((Boolean,), QVariant.Bool),
]


def _sa_type_to_qvariant(column_type: Any) -> object:
    for types, qv in _TYPE_MAP:
        if isinstance(column_type, types):
            return qv
    return QVariant.String


def create_other_layers(_iface: Any) -> None:
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
                    if cfg.get('layer') == layer.name():
                        model_name = cfg.get('model')
                        break

                model_class = getattr(_models, model_name, None) if model_name else None
                if model_class is None:
                    continue
                fields = []
                for column_name, column_obj in model_class.__table__.columns.items():
                    if isinstance(column_obj.type, Geometry):
                        continue

                    field_type = _sa_type_to_qvariant(column_obj.type)
                    fields.append(QgsField(column_name, field_type))

                layer.startEditing()
                provider = layer.dataProvider()
                provider.addAttributes(fields)
                layer.updateFields()
                layer.commitChanges()
                layer.triggerRepaint()


def _commune_id_from_code(commune_code: str) -> int | None:
    """Resolve commune_id from commune_code using communes.json."""
    try:
        with Path(COMMUNES_JSON).open(encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning('could not load %s: %s', COMMUNES_JSON, e)
        return None
    for c in data.values():
        v = c.get('commune_code')
        if v is not None and int(v) == int(commune_code):
            commune_id = int(c.get('commune_id', 0))
            logger.info(
                'matched commune_code=%s -> commune_id=%s',
                v,
                commune_id,
            )
            return commune_id
    logger.warning('commune_code=%s not found in communes.json', commune_code)
    return None


def _wkt_from_commune_id(commune_id: int) -> str | None:
    """Read geometry WKT from communes.db for a given commune_id."""
    try:
        with sqlite3.connect(COMMUNES_DB) as conn:
            sql = 'SELECT wkt FROM geometries WHERE commune_id = ?'
            row = conn.execute(sql, (commune_id,)).fetchone()
    except sqlite3.Error as e:
        logger.warning('could not query %s: %s', COMMUNES_DB, e)
        return None
    if row:
        logger.info('WKT from DB, len=%s', len(row[0]))
        return row[0]
    logger.warning('commune_id=%s not found in communes.db', commune_id)
    return None


def _resolve_commune_geometry() -> QgsGeometry:
    """Resolve the commune geometry from the authenticated user's commune_code."""
    user_data = get_current_user()
    commune_code = user_data.get('commune_code') if user_data else None

    if not commune_code:
        logger.info('init_allowed_zone: no commune_code, skipping geometry lookup')
        return QgsGeometry()

    commune_id = _commune_id_from_code(commune_code)
    if commune_id is None:
        return QgsGeometry()

    wkt = _wkt_from_commune_id(commune_id)
    if not wkt:
        return QgsGeometry()

    multipolygon = QgsGeometry.fromWkt(wkt)
    logger.info(
        'init_allowed_zone: geometry empty=%s isValid=%s',
        multipolygon.isEmpty(),
        multipolygon.isGeosValid(),
    )
    return multipolygon


def _set_layer_geometry(layer: QgsVectorLayer, multipolygon: QgsGeometry) -> None:
    """Replace *layer* features with a single *multipolygon* feature."""
    layer.startEditing()
    provider = layer.dataProvider()
    provider.deleteFeatures([f.id() for f in layer.getFeatures()])
    if multipolygon and not multipolygon.isEmpty():
        feature = QgsFeature()
        feature.setGeometry(multipolygon)
        provider.addFeature(feature)
    layer.commitChanges()
    layer.updateExtents()
    layer.triggerRepaint()


def _create_municipality_layer(multipolygon: QgsGeometry) -> QgsVectorLayer:
    """Create a new municipality boundary layer and add it to the project."""
    layer = QgsVectorLayer(
        f'MultiPolygon?crs={CRS}', LAYER_MUNICIPALITY, MEMORY_PROVIDER
    )
    layer.setMinimumScale(10000000)
    logger.info('init_allowed_zone: layer valid=%s', layer.isValid())
    provider = layer.dataProvider()
    layer.updateFields()
    if multipolygon and not multipolygon.isEmpty():
        feature = QgsFeature()
        feature.setGeometry(multipolygon)
        provider.addFeature(feature)
    layer.updateExtents()
    symbol = QgsFillSymbol.createSimple(
        {'color': 'transparent', 'outline_color': 'red', 'outline_width': '0.5'}
    )
    layer.renderer().setSymbol(symbol)
    QgsProject.instance().addMapLayer(layer)
    root = QgsProject.instance().layerTreeRoot()
    logger.info(
        'init_allowed_zone: tree children=%s', [c.name() for c in root.children()]
    )
    return layer


def _log_municipality_diagnostics() -> None:
    """Log final diagnostics for the municipality layer."""
    root = QgsProject.instance().layerTreeRoot()
    final_names = [c.name() for c in root.children()]
    logger.info('init_allowed_zone: FINAL tree children=%s', final_names)
    mun_layers = QgsProject.instance().mapLayersByName(LAYER_MUNICIPALITY)
    if mun_layers:
        mun_layer = mun_layers[0]
        logger.info(
            'init_allowed_zone: feature count=%s extent=%s',
            mun_layer.featureCount(),
            mun_layer.extent().toString(),
        )


def init_allowed_zone(iface: Any) -> None:
    """Create the municipality boundary layer from the authenticated user."""
    multipolygon = _resolve_commune_geometry()

    existing_layers = QgsProject.instance().mapLayersByName(LAYER_MUNICIPALITY)
    if existing_layers:
        logger.info('init_allowed_zone: updating existing layer')
        _set_layer_geometry(existing_layers[0], multipolygon)
    else:
        logger.info('init_allowed_zone: creating new layer')
        _create_municipality_layer(multipolygon)

    if multipolygon and not multipolygon.isEmpty():
        iface.mapCanvas().zoomToFeatureExtent(multipolygon.boundingBox())
    iface.mapCanvas().refresh()

    create_other_layers(iface)
    _log_municipality_diagnostics()
