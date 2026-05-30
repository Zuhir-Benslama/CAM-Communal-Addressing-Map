"""Layer creation and initialization utilities."""
import json
import logging
import sqlite3
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
from ..constants import CRS, COOKIE_FILE, LAYER_MUNICIPALITY, MEMORY_PROVIDER, COMMUNES_DB, COMMUNES_JSON

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
    logger.info("init_allowed_zone: user_data=%s", user_data)
    commune_code = user_data.get('commune_code') if user_data else None
    logger.info("init_allowed_zone: commune_code=%s", commune_code)

    wkt = None
    if commune_code:
        commune_id = None
        try:
            with open(COMMUNES_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("init_allowed_zone: communes.json has %d entries", len(data))
            for c in data.values():
                v = c.get('commune_code')
                if v is not None and int(v) == int(commune_code):
                    commune_id = int(c.get('commune_id', 0))
                    logger.info("init_allowed_zone: matched commune_code=%s -> commune_id=%s", v, commune_id)
                    break
            if commune_id is None:
                logger.warning("init_allowed_zone: commune_code=%s not found in communes.json", commune_code)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("init_allowed_zone: could not load %s: %s", COMMUNES_JSON, e)
        if commune_id:
            try:
                with sqlite3.connect(COMMUNES_DB) as conn:
                    cur = conn.execute('SELECT wkt FROM geometries WHERE commune_id = ?', (commune_id,))
                    row = cur.fetchone()
                if row:
                    wkt = row[0]
                    logger.info("init_allowed_zone: WKT from DB, len=%s", len(wkt))
                else:
                    logger.warning("init_allowed_zone: commune_id=%s not found in communes.db", commune_id)
            except sqlite3.Error as e:
                logger.warning("init_allowed_zone: could not query %s: %s", COMMUNES_DB, e)
    else:
        logger.info("init_allowed_zone: no commune_code, skipping geometry lookup")

    if wkt:
        multipolygon = QgsGeometry.fromWkt(wkt)
        logger.info("init_allowed_zone: geometry empty=%s isValid=%s",
                     multipolygon.isEmpty(), multipolygon.isGeosValid())
    else:
        multipolygon = QgsGeometry()
        logger.info("init_allowed_zone: no wkt, empty geometry")

    existing_layers = (
        QgsProject.instance()
        .mapLayersByName(LAYER_MUNICIPALITY)
    )

    if existing_layers:
        logger.info("init_allowed_zone: updating existing layer")
        layer = existing_layers[0]
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
    else:
        logger.info("init_allowed_zone: creating new layer")
        layer = QgsVectorLayer(
            f'MultiPolygon?crs={CRS}',
            LAYER_MUNICIPALITY,
            MEMORY_PROVIDER
        )
        layer.setMinimumScale(10000000)
        logger.info("init_allowed_zone: layer valid=%s", layer.isValid())
        provider = layer.dataProvider()
        layer.updateFields()
        if multipolygon and not multipolygon.isEmpty():
            feature = QgsFeature()
            feature.setGeometry(multipolygon)
            provider.addFeature(feature)
        layer.updateExtents()
        symbol = QgsFillSymbol.createSimple({
            'color': 'transparent',
            'outline_color': 'red',
            'outline_width': '0.5'
        })
        layer.renderer().setSymbol(symbol)
        QgsProject.instance().addMapLayer(layer)
        root = QgsProject.instance().layerTreeRoot()
        logger.info("init_allowed_zone: tree children=%s",
                     [c.name() for c in root.children()])

    if multipolygon and not multipolygon.isEmpty():
        iface.mapCanvas().zoomToFeatureExtent(
            multipolygon.boundingBox()
        )
    iface.mapCanvas().refresh()

    create_other_layers(iface)

    # Final diagnostics
    root = QgsProject.instance().layerTreeRoot()
    final_names = [c.name() for c in root.children()]
    logger.info("init_allowed_zone: FINAL tree children=%s", final_names)
    mun_layers = QgsProject.instance().mapLayersByName(LAYER_MUNICIPALITY)
    if mun_layers:
        mun_layer = mun_layers[0]
        logger.info("init_allowed_zone: feature count=%s extent=%s",
                     mun_layer.featureCount(),
                     mun_layer.extent().toString())
