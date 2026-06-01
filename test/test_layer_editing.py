"""Tests for layer/editing.py."""
import importlib
import sys
import unittest
from unittest.mock import patch

from .helpers import (
    make_mock_iface,
    make_mock_layer,
    setup_mocks,
    wire_module_attributes,
)


class TestEditing(unittest.TestCase):
    """Test layer editing functions."""

    @classmethod
    def setUpClass(cls):
        setup_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.layer.editing', 'layer/editing.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.layer.editing'] = cls.mod
        spec.loader.exec_module(cls.mod)
        wire_module_attributes()

    def setUp(self):
        self.iface = make_mock_iface()
        self.layer = make_mock_layer()

    def test_activate_add_feature_point(self):
        self.layer.geometryType.return_value = 0
        self.mod._activate_add_feature(self.iface, self.layer)
        self.layer.startEditing.assert_called_once()
        self.iface.actionAddFeature().trigger.assert_called_once()

    def test_activate_add_feature_line(self):
        self.layer.geometryType.return_value = 1
        self.mod._activate_add_feature(self.iface, self.layer)
        self.layer.startEditing.assert_called_once()
        self.iface.actionAddFeature().trigger.assert_called_once()

    def test_activate_add_feature_polygon(self):
        self.layer.geometryType.return_value = 2
        self.mod._activate_add_feature(self.iface, self.layer)
        self.layer.startEditing.assert_called_once()
        self.iface.actionAddFeature().trigger.assert_called_once()

    def test_edit_line_layer_with_active_layer(self):
        self.iface.activeLayer.return_value = self.layer
        self.mod.edit_line_layer(self.iface)
        self.layer.startEditing.assert_called_once()

    def test_edit_line_layer_no_active_layer(self):
        self.iface.activeLayer.return_value = None
        self.mod.edit_line_layer(self.iface)
        self.iface.messageBar().pushMessage.assert_called_once()

    def test_save_changes_success(self):
        self.iface.activeLayer.return_value = self.layer
        self.layer.isEditable.return_value = True
        self.layer.commitChanges.return_value = True
        self.mod.save_changes(self.iface)
        self.layer.commitChanges.assert_called_once()

    def test_save_changes_no_layer(self):
        self.iface.activeLayer.return_value = None
        self.mod.save_changes(self.iface)
        self.iface.messageBar().pushMessage.assert_called_once()

    def test_save_changes_not_editable(self):
        self.iface.activeLayer.return_value = self.layer
        self.layer.isEditable.return_value = False
        self.mod.save_changes(self.iface)
        self.layer.commitChanges.assert_not_called()

    def test_save_changes_failure(self):
        self.iface.activeLayer.return_value = self.layer
        self.layer.isEditable.return_value = True
        self.layer.commitChanges.return_value = False
        self.mod.save_changes(self.iface)
        self.iface.messageBar().pushMessage.assert_called_once()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_start_editing_layer_found(self, mock_project):
        (mock_project.instance.return_value
    .mapLayersByName.return_value) = [self.layer]
        self.mod.start_editing_layer(self.iface, 'test_layer')
        self.iface.setActiveLayer.assert_called_once_with(self.layer)
        self.layer.startEditing.assert_called_once()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_start_editing_layer_not_found(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.start_editing_layer(self.iface, 'nonexistent')
        self.iface.messageBar().pushMessage.assert_called_once()
        self.layer.startEditing.assert_not_called()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_stop_editing_layer_success(self, mock_project):
        (mock_project.instance.return_value
    .mapLayersByName.return_value) = [self.layer]
        self.layer.isEditable.return_value = True
        self.mod.stop_editing_layer(self.iface, 'test_layer')
        self.layer.commitChanges.assert_called_once()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_stop_editing_layer_not_found(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.stop_editing_layer(self.iface, 'nonexistent')
        self.iface.messageBar().pushMessage.assert_called_once()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_stop_editing_layer_not_editable(self, mock_project):
        (mock_project.instance.return_value
    .mapLayersByName.return_value) = [self.layer]
        self.layer.isEditable.return_value = False
        self.mod.stop_editing_layer(self.iface, 'test_layer')
        self.layer.commitChanges.assert_not_called()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_update_layer_enables_vertex_tool(self, mock_project):
        (mock_project.instance.return_value
    .mapLayersByName.return_value) = [self.layer]
        self.mod.update_layer(self.iface, 'test_layer')
        self.iface.setActiveLayer.assert_called_once_with(self.layer)
        self.iface.actionVertexTool().trigger.assert_called_once()

    @patch('plans_adressage.layer.editing.QgsProject')
    def test_update_layer_not_found(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.update_layer(self.iface, 'nonexistent')
        self.iface.actionVertexTool.assert_not_called()


if __name__ == '__main__':
    unittest.main()
