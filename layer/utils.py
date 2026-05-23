"""Layer creation and initialization utilities."""
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
from ..app.users.repository import qgis_config
from ..app.core.database import get_session
from ..app.users.models import User
from ..app.orders.models import Localite
from ..constants import CRS, COOKIE_FILE, LAYER_MUNICIPALITY, MEMORY_PROVIDER

logger = logging.getLogger(__name__)


def create_other_layers(iface) -> None:
    """Create non-mapper vector layers from QGIS config."""
    other_layer_list = qgis_config().get('other_layers')
    mapper = qgis_config().get('mapper')
    for layer_cfg in other_layer_list:
        layer = QgsVectorLayer(layer_cfg.get('url'), layer_cfg.get('label'), MEMORY_PROVIDER)
        if layer.isValid():
            existing = QgsProject.instance().mapLayersByName(layer_cfg.get('label'))
            if not existing:
                QgsProject.instance().addMapLayer(layer)
                model_name = None
                for cfg in mapper:
                    if cfg.get("layer") == layer.name():
                        model_name = cfg.get("model")
                        break

                model_class = getattr(_models, model_name, None)
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
    filename = COOKIE_FILE

    with open(filename, 'r', encoding='utf-8') as f:
        cookie_data = toml.load(f)
    cookie = cookie_data.get('Session', {}).get('cookie', None)
    uid = cookie_data.get('Session', {}).get('uid', None)
    if cookie and uid:
        session = get_session()
        try:
            user = (
                session.query(User)
                .filter(
                    User.id == uid, User.api_key == cookie, User.active.is_(True)
                )
                .first()
            )

            if user:
                localite = (
                    session.query(Localite)
                    .filter(Localite.pk_uid == user.affectation_id)
                    .first()
                )
            else:
                localite = None

            wkt = None
            if localite:
                row = session.query(
                    func.ST_AsText(localite.geometry)
                ).first()
                wkt = str(row[0]) if row else ""

            if localite and wkt:
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
        finally:
            session.close()
