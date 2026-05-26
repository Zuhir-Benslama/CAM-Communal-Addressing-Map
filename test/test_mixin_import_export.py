"""Tests for mixins/import_export_mixin.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks


class TestImportExportMixin(unittest.TestCase):
    """Test ImportExportMixin map rendering and export."""

    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.import_export_mixin',
            'mixins/import_export_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.import_export_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.ImportExportMixin()
        self.mixin._tr = lambda s: s
        self.mixin.north = MagicMock()
        self.mixin.scale = MagicMock()
        self.mixin.map_situation = MagicMock()
        self.mixin.symbols = MagicMock(return_value={'legend': 'data'})
        self.mixin.iface = MagicMock()
        self.mixin.type_plan = 'Numbering'
        self.mixin.type_to_hide = 'Panels'
        self.mixin.current_user = {'wilaya': '16', 'commune': 'Alger Centre'}
        self.mixin.dateEdit = MagicMock()
        self.mixin.dateEdit.date().toString = MagicMock(
            return_value='2026/05/21')
        self.mixin.lineEdit_by = MagicMock()
        self.mixin.lineEdit_by.text = MagicMock(return_value='admin')
        self.mixin.lineEdit_type = MagicMock()
        self.mixin.lineEdit_type.text = MagicMock(return_value='Zone A')
        self.mixin.lineEdit_nummokh = MagicMock()
        self.mixin.lineEdit_nummokh.text = MagicMock(return_value='001')

    def mock_canvas(self, scale_value=1000):
        canvas = MagicMock()
        canvas.extent.return_value.scale = MagicMock()
        canvas.layers.return_value = []
        (canvas.mapSettings.return_value
         .destinationCrs.return_value) = MagicMock()
        canvas.scale.return_value = scale_value
        self.mixin.iface.mapCanvas = MagicMock(return_value=canvas)
        return canvas

    def test_render_and_export_missing_type_plan(self):
        self.mixin.type_plan = None
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._render_and_export('3')
            mock_mb.critical.assert_called_once()

    def test_render_and_export_missing_type_to_hide(self):
        self.mixin.type_to_hide = None
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._render_and_export('3')
            mock_mb.critical.assert_called_once()

    def test_render_and_export_renders_and_saves(self):
        self.mock_canvas(scale_value=2500)

        mock_image = MagicMock()
        mock_image.save = MagicMock(return_value=True)
        mock_job = MagicMock()
        mock_job.renderedImage.return_value = mock_image
        mock_job.waitForFinished = MagicMock()

        with patch.object(self.mod, 'QgsMapRendererParallelJob',
                          return_value=mock_job), \
             patch.object(self.mod, 'QgsMapSettings') as mock_settings, \
             patch.object(self.mod, 'validate_text',
                          return_value='valid'), \
             patch.object(self.mod, 'json') as mock_json, \
             patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._render_and_export('3')

            self.mixin.north.assert_called_once()
            self.mixin.scale.assert_called_once()
            self.mixin.map_situation.assert_not_called()
            mock_settings.return_value.setLayers.assert_called_once()
            mock_settings.return_value.setExtent.assert_called_once()
            mock_settings.return_value.setOutputSize.assert_called_once_with(
                self.mod.EXPORT_MAP_SIZE)
            mock_job.start.assert_called_once()
            mock_job.waitForFinished.assert_called_once()
            mock_image.save.assert_called_once()
            mock_json.dump.assert_called_once()
            mock_mb.information.assert_called_once()

    def test_render_and_export_with_include_situation(self):
        self.mock_canvas()

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)
        mock_job.waitForFinished = MagicMock()

        with patch.object(self.mod, 'QgsMapRendererParallelJob',
                          return_value=mock_job), \
             patch.object(self.mod, 'QgsMapSettings'), \
             patch.object(self.mod, 'validate_text', return_value='valid'), \
             patch.object(self.mod, 'json'), \
             patch.object(self.mod, 'QMessageBox'):
            self.mixin._render_and_export('4', include_situation=True)
            self.mixin.map_situation.assert_called_once()

    def test_render_and_export_image_save_failure(self):
        self.mock_canvas()

        mock_image = MagicMock()
        mock_image.save = MagicMock(return_value=False)
        mock_job = MagicMock()
        mock_job.renderedImage.return_value = mock_image
        mock_job.waitForFinished = MagicMock()

        with patch.object(self.mod, 'QgsMapRendererParallelJob',
                          return_value=mock_job), \
             patch.object(self.mod, 'QgsMapSettings'):
            self.mixin._render_and_export('3')
            mock_image.save.assert_called_once()

    def test_render_and_export_no_symbols_skips_json(self):
        self.mock_canvas()
        self.mixin.symbols = MagicMock(return_value=None)

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)
        mock_job.waitForFinished = MagicMock()

        with patch.object(self.mod, 'QgsMapRendererParallelJob',
                          return_value=mock_job), \
             patch.object(self.mod, 'QgsMapSettings'), \
             patch.object(self.mod, 'json') as mock_json:
            self.mixin._render_and_export('3')
            mock_json.dump.assert_not_called()

    def test_render_and_export_json_write_failure_logged(self):
        self.mock_canvas()

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)
        mock_job.waitForFinished = MagicMock()

        with patch.object(self.mod, 'QgsMapRendererParallelJob',
                          return_value=mock_job), \
             patch.object(self.mod, 'QgsMapSettings'), \
             patch.object(self.mod, 'validate_text', return_value='valid'), \
             patch.object(self.mod, 'json') as mock_json:
            mock_json.dump = MagicMock(side_effect=OSError('write error'))
            # Should not raise despite JSON write failure
            self.mixin._render_and_export('3')

    def test_export_to_image1_a0(self):
        self.mixin.paper = MagicMock()
        self.mixin.paper.currentData = MagicMock(return_value='A0')
        with patch.object(self.mixin, '_render_and_export') as mock_render:
            self.mixin.export_to_image()
            mock_render.assert_called_once_with('4', include_situation=True)

    def test_export_to_image1_a3(self):
        self.mixin.paper = MagicMock()
        self.mixin.paper.currentData = MagicMock(return_value='A3')
        with patch.object(self.mixin, '_render_and_export') as mock_render:
            self.mixin.export_to_image()
            mock_render.assert_called_once_with('3')

    def test_export_to_image1_other(self):
        self.mixin.paper = MagicMock()
        self.mixin.paper.currentData = MagicMock(return_value='A4')
        with patch.object(self.mixin, '_render_and_export') as mock_render:
            self.mixin.export_to_image()
            mock_render.assert_not_called()


if __name__ == '__main__':
    unittest.main()
