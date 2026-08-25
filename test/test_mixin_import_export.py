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
        self.mixin._output_dir = '/tmp/pytest_output'
        self.mixin.current_user = {
            'wilaya': '16',
            'commune': 'Alger Centre',
            'first_name': 'Admin',
            'last_name': 'User',
        }
        self._subprocess_run = self.mod.subprocess.run
        self.mod.subprocess.run = MagicMock(return_value=MagicMock())
        self._run_reporting = self.mod.run_reporting_script
        self.mod.run_reporting_script = MagicMock(return_value=None)

    def tearDown(self):
        self.mod.subprocess.run = self._subprocess_run
        self.mod.run_reporting_script = self._run_reporting
        self.mixin._export_in_progress = False
        self.mixin._render_job = None
        self.mixin._export_method = None

    def _finish_render(self, mock_job):
        """Simulate the async render job completing."""
        handler = mock_job.jobFinished.connect.call_args[0][0]
        handler()

    def mock_canvas(self, scale_value=1000):
        canvas = MagicMock()
        canvas.extent.return_value.scale = MagicMock()
        canvas.layers.return_value = []
        (canvas.mapSettings.return_value.destinationCrs.return_value) = MagicMock()
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
        canvas = self.mock_canvas(scale_value=2500)
        ms = canvas.mapSettings.return_value

        mock_image = MagicMock()
        mock_image.save = MagicMock(return_value=True)
        mock_job = MagicMock()
        mock_job.renderedImage.return_value = mock_image

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'validate_text', return_value='valid'),
            patch.object(self.mod, 'json') as mock_json,
            patch.object(self.mod, 'QMessageBox') as mock_mb,
        ):
            self.mixin._render_and_export('3')

            self.mixin.north.assert_called_once()
            self.mixin.scale.assert_called_once()
            self.mixin.map_situation.assert_not_called()
            ms.setExtent.assert_called_once()
            ms.setOutputSize.assert_called_once_with(self.mod.EXPORT_MAP_SIZE)
            ms.setFlag.assert_called_once()
            mock_job.start.assert_called_once()
            mock_job.waitForFinished.assert_not_called()

            # Simulate the render finishing; export continues.
            self._finish_render(mock_job)

            mock_image.save.assert_called_once()
            mock_json.dump.assert_called_once()
            mock_mb.information.assert_called_once()

    def test_render_and_export_with_include_situation(self):
        self.mock_canvas()

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'QgsMapSettings'),
            patch.object(self.mod, 'validate_text', return_value='valid'),
            patch.object(self.mod, 'json'),
            patch.object(self.mod, 'QMessageBox'),
        ):
            self.mixin._render_and_export('4', include_situation=True)
            self.mixin.map_situation.assert_called_once()

    def test_render_and_export_image_save_failure(self):
        self.mock_canvas()

        mock_image = MagicMock()
        mock_image.save = MagicMock(return_value=False)
        mock_job = MagicMock()
        mock_job.renderedImage.return_value = mock_image

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'QgsMapSettings'),
            patch.object(self.mod, 'json') as mock_json,
        ):
            self.mixin._render_and_export('3')
            self._finish_render(mock_job)
            mock_image.save.assert_called_once()
            mock_json.dump.assert_not_called()

    def test_render_and_export_no_symbols_skips_json(self):
        self.mock_canvas()
        self.mixin.symbols = MagicMock(return_value=None)

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'QgsMapSettings'),
            patch.object(self.mod, 'json') as mock_json,
        ):
            self.mixin._render_and_export('3')
            self._finish_render(mock_job)
            mock_json.dump.assert_not_called()

    def test_render_and_export_json_write_failure_logged(self):
        self.mock_canvas()

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'QgsMapSettings'),
            patch.object(self.mod, 'validate_text', return_value='valid'),
            patch.object(self.mod, 'json') as mock_json,
        ):
            mock_json.dump = MagicMock(side_effect=OSError('write error'))
            # Should not raise despite JSON write failure
            self.mixin._render_and_export('3')
            self._finish_render(mock_job)

    def test_render_and_export_reentrant_call_ignored(self):
        self.mock_canvas()
        # Exit the completion callback early; this test only checks
        # that overlapping requests are ignored.
        self.mixin.symbols = MagicMock(return_value=None)

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ) as mock_job_cls,
            patch.object(self.mod, 'QgsMapSettings'),
        ):
            self.mixin._render_and_export('3')
            # Second request while the render is still running is ignored.
            self.mixin._render_and_export('3')
            self.assertEqual(mock_job_cls.call_count, 1)

            self._finish_render(mock_job)
            # After completion a new export may start.
            self.mixin._render_and_export('3')
            self.assertEqual(mock_job_cls.call_count, 2)

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

    def test_build_export_data_no_user(self):
        self.mixin.current_user = None
        self.assertIsNone(self.mixin._build_export_data())

    def test_validate_export_data_missing_keys(self):
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            result = self.mixin._validate_export_data({'type_plan': 'Numbering'})
            self.assertFalse(result)
            mock_mb.critical.assert_called_once()

    def test_validate_export_data_complete(self):
        data = {
            'type_plan': 'Numbering',
            'num_plan': '1',
            'scale': '1:1000',
            'by': 'Admin',
            'date': '2026/01/01',
        }
        self.assertTrue(self.mixin._validate_export_data(data))

    def test_render_and_export_no_current_user_skips_script(self):
        self.mixin.current_user = None
        self.mock_canvas()

        mock_job = MagicMock()
        mock_job.renderedImage.return_value.save = MagicMock(return_value=True)
        mock_job.waitForFinished = MagicMock()

        with (
            patch.object(
                self.mod, 'QgsMapRendererSequentialJob', return_value=mock_job
            ),
            patch.object(self.mod, 'QgsMapSettings'),
            patch.object(self.mod, 'validate_text', return_value='valid'),
        ):
            self.mixin._render_and_export('3')
        self.mod.run_reporting_script.assert_not_called()

    def test_invoke_reporting_script_process_error(self):
        import subprocess

        err = subprocess.CalledProcessError(2, 'cmd')
        err.stderr = 'boom'
        self.mod.run_reporting_script.side_effect = err
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._invoke_reporting_script('3')
            mock_mb.critical.assert_called_once()
            self.assertIn('boom', mock_mb.critical.call_args[0][2])

    def test_invoke_reporting_script_process_error_no_output(self):
        import subprocess

        err = subprocess.CalledProcessError(2, 'cmd')
        err.stderr = None
        self.mod.run_reporting_script.side_effect = err
        with patch.object(self.mod, 'QMessageBox'):
            self.mixin._invoke_reporting_script('3')

    def test_invoke_reporting_script_oserror(self):
        self.mod.run_reporting_script.side_effect = OSError('spawn failed')
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._invoke_reporting_script('3')
            mock_mb.critical.assert_called_once()


if __name__ == '__main__':
    unittest.main()
