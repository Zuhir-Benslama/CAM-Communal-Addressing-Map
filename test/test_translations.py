"""Safe Translations Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import os
import unittest

from qgis.PyQt.QtCore import QCoreApplication, QTranslator

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()[0]


@unittest.skipIf(QGIS_APP is None, 'QGIS not available')
class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if 'LANG' in os.environ:
            del os.environ['LANG']

    def tearDown(self):
        """Runs after each test."""
        if 'LANG' in os.environ:
            del os.environ['LANG']

    def test_qgis_translations(self):
        """Test that translations work."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(dir_path, 'i18n', 'af.qm')
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = 'Goeie more'
        real_message = QCoreApplication.translate('@default', 'Good morning')
        self.assertEqual(real_message, expected_message)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(SafeTranslationsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
