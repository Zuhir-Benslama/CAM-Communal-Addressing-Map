"""Tests for QGIS functionality.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 3 of the License, or
     (at your option) any later version.

"""

import importlib
import os
import sys
import unittest

from unittest.mock import MagicMock

from .utilities import get_qgis_app

_real_qgis_core = None


def _ensure_real_qgis():
    """Load the real qgis.core, keeping it for the lifetime of this module."""
    global _real_qgis_core
    if _real_qgis_core is not None:
        return
    core = sys.modules.get('qgis.core')
    if not isinstance(core, MagicMock):
        _real_qgis_core = core
        return
    saved = {}
    for key in (
        'qgis',
        'qgis.core',
        'qgis.gui',
        'qgis.PyQt',
        'qgis.PyQt.QtCore',
        'qgis.PyQt.QtGui',
        'qgis.PyQt.QtWidgets',
    ):
        if key in sys.modules:
            saved[key] = sys.modules.pop(key)
    try:
        importlib.import_module('qgis.core')
        _real_qgis_core = sys.modules.get('qgis.core')
    except ImportError:
        pass
    sys.modules.update(saved)


QGIS_APP = get_qgis_app()[0]


@unittest.skipIf(QGIS_APP is None, 'QGIS not available')
class QGISTest(unittest.TestCase):
    """Test the QGIS Environment"""

    def test_qgis_environment(self):
        """QGIS environment has the expected providers"""
        _ensure_real_qgis()
        if _real_qgis_core is None:
            self.skipTest('Real QGIS core not available')
        r = _real_qgis_core.QgsProviderRegistry.instance()
        self.assertIn('gdal', r.providerList())
        self.assertIn('ogr', r.providerList())

    def test_projection(self):
        """Test that QGIS properly parses a wkt string."""
        _ensure_real_qgis()
        if _real_qgis_core is None:
            self.skipTest('Real QGIS core not available')
        crs = _real_qgis_core.QgsCoordinateReferenceSystem()
        wkt = (
            'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",'
            'SPHEROID["WGS_1984",6378137.0,298.257223563]],'
            'PRIMEM["Greenwich",0.0],UNIT["Degree",'
            '0.0174532925199433]]'
        )
        crs.createFromWkt(wkt)
        auth_id = crs.authid()
        self.assertIn(auth_id, ('EPSG:4326', 'OGC:CRS84'))

        # now test for a loaded layer
        path = os.path.join(os.path.dirname(__file__), 'tenbytenraster.asc')
        title = 'TestRaster'
        layer = _real_qgis_core.QgsRasterLayer(path, title)
        auth_id = layer.crs().authid()
        self.assertIn(auth_id, ('EPSG:4326', 'OGC:CRS84'))


if __name__ == '__main__':
    unittest.main()
