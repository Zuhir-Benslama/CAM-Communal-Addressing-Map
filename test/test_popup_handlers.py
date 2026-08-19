"""Tests for gui.popup_handlers."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


def _load_module():
    setup_gui_mocks()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.popup_handlers',
        'gui/popup_handlers.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.gui.popup_handlers'] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_dialog(**overrides):
    d = MagicMock()
    d._current_form_data = {}
    d._tr_locale = 'en'
    d.iface = MagicMock()
    d.attribute = 'rec-1'
    d._ref_id = None
    d._ref_layer = None
    for k, v in overrides.items():
        setattr(d, k, v)
    return d


def _patch_constants(mod):
    """Return a context manager that patches locale_value and validate_text."""

    def _locale_value(instance, field_base, locale=''):
        if locale == 'ar':
            return getattr(instance, field_base, '') or ''
        field = f'{field_base}_{locale}'
        val = getattr(instance, field, None)
        return val if val else (getattr(instance, field_base, '') or '')

    def _validate_text(value, max_length=255):
        value = value.strip()
        if len(value) > max_length:
            value = value[:max_length]
        return value

    return (
        patch.object(mod, 'locale_value', side_effect=_locale_value),
        patch.object(mod, 'validate_text', side_effect=_validate_text),
    )


class TestPopulateHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_populate_name_type_returns_name_and_type(self):
        query = MagicMock()
        query.type = 'residential'
        query.name_fr = 'Main Street'
        result = self.mod._populate_name_type(query, 'fr')
        self.assertEqual(result['name'], 'Main Street')
        self.assertEqual(result['type'], 'residential')

    def test_populate_name_type_ar_fallback(self):
        query = MagicMock()
        query.type = 'commercial'
        del query.name_ar
        query.name = 'Sharia'
        result = self.mod._populate_name_type(query, 'ar')
        self.assertEqual(result['name'], 'Sharia')
        self.assertEqual(result['type'], 'commercial')

    def test_populate_name_type_locale_fallback(self):
        query = MagicMock()
        query.type = 'industrial'
        del query.name_fr
        query.name = 'Zone Industrielle'
        result = self.mod._populate_name_type(query, 'fr')
        self.assertEqual(result['name'], 'Zone Industrielle')

    def test_populate_road_delegates(self):
        query = MagicMock()
        query.type = 'Avenue'
        query.name_fr = 'Avenue Mohammed V'
        result = self.mod.populate_road(MagicMock(), query, 'fr')
        self.assertEqual(result['type'], 'Avenue')
        self.assertEqual(result['name'], 'Avenue Mohammed V')
        self.assertIn('name', result)
        self.assertIn('type', result)

    def test_populate_facility_includes_category(self):
        query = MagicMock()
        query.type = 'School'
        query.name_fr = 'El Irfane'
        query.category = 'education'
        result = self.mod.populate_facility(MagicMock(), query, 'fr')
        self.assertEqual(result['type'], 'School')
        self.assertEqual(result['name'], 'El Irfane')
        self.assertEqual(result['category'], 'education')
        self.assertEqual(len(result), 3)

    def test_populate_subdivision_delegates(self):
        query = MagicMock()
        query.type = 'Cite'
        query.name = 'Cite 500'
        result = self.mod.populate_subdivision(MagicMock(), query, 'en')
        self.assertEqual(result['type'], 'Cite')
        self.assertIn('name', result)

    def test_populate_zone_delegates(self):
        query = MagicMock()
        query.type = 'Zone'
        query.name = 'Zone A'
        result = self.mod.populate_zone(MagicMock(), query, 'en')
        self.assertEqual(result['type'], 'Zone')
        self.assertIn('name', result)


class TestPopulateNumbering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def _make_numbering_query(self, **overrides):
        q = MagicMock()
        q.value = '42'
        q.repetition = 'bis'
        q.state = 'booked'
        q.road_id = None
        q.subdivision_id = None
        q.activity_cat = 'residential'
        q.activity_type = 'house'
        q.road = MagicMock()
        q.road.type = 'Avenue'
        q.road.type_en = 'Avenue'
        q.road.name = 'Hassan II'
        q.road.name_en = 'Hassan II'
        q.subdivision = MagicMock()
        q.subdivision.name = 'Cite 500'
        q.subdivision.name_en = 'Cite 500'
        for k, v in overrides.items():
            setattr(q, k, v)
        return q

    def test_base_fields(self):
        q = self._make_numbering_query()
        result = self.mod.populate_numbering(MagicMock(), q, 'en')
        self.assertEqual(result['number'], '42')
        self.assertEqual(result['repetition'], 'bis')
        self.assertEqual(result['state'], 'booked')
        self.assertEqual(result['activityCat'], 'residential')
        self.assertEqual(result['activityType'], 'house')

    def test_with_road(self):
        q = self._make_numbering_query(road_id='road-123', subdivision_id=None)
        result = self.mod.populate_numbering(MagicMock(), q, 'en')
        self.assertEqual(result['refType'], 'roads')
        self.assertIn('Avenue', result['refName'])
        self.assertIn('Hassan II', result['refName'])

    def test_with_subdivision(self):
        q = self._make_numbering_query(road_id=None, subdivision_id='sub-1')
        result = self.mod.populate_numbering(MagicMock(), q, 'en')
        self.assertEqual(result['refType'], 'subdivisions')
        self.assertEqual(result['refName'], 'Cite 500')
        self.assertNotIn('refType', result) if 'refType' not in result else None

    def test_both_none_no_ref(self):
        q = self._make_numbering_query(road_id=None, subdivision_id=None)
        result = self.mod.populate_numbering(MagicMock(), q, 'en')
        self.assertNotIn('refType', result)
        self.assertNotIn('refName', result)

    def test_empty_fallbacks(self):
        q = self._make_numbering_query(value='', repetition='', state='')
        q.activity_cat = ''
        q.activity_type = ''
        result = self.mod.populate_numbering(MagicMock(), q, 'en')
        self.assertEqual(result['number'], '')
        self.assertEqual(result['repetition'], '')
        self.assertEqual(result['state'], '')
        self.assertEqual(result['activityCat'], '')
        self.assertEqual(result['activityType'], '')


class TestPopulatePanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def _make_panel_query(self, **overrides):
        q = MagicMock()
        q.status = 'mounted'
        q.road_id = None
        q.organization_id = None
        q.subdivision_id = None
        q.road = MagicMock()
        q.road.type = 'Boulevard'
        q.road.type_en = 'Boulevard'
        q.road.name = 'Didouche Mourad'
        q.road.name_en = 'Didouche Mourad'
        q.organization = MagicMock()
        q.organization.type = 'Hospital'
        q.organization.type_en = 'Hospital'
        q.organization.name = 'CHU'
        q.organization.name_en = 'CHU'
        q.subdivision = MagicMock()
        q.subdivision.name = 'Cite Nord'
        q.subdivision.name_en = 'Cite Nord'
        for k, v in overrides.items():
            setattr(q, k, v)
        return q

    def test_base_status(self):
        q = self._make_panel_query()
        result = self.mod.populate_panel(MagicMock(), q, 'en')
        self.assertEqual(result['mountStatus'], 'mounted')

    def test_with_road(self):
        q = self._make_panel_query(
            road_id='r1', organization_id=None, subdivision_id=None
        )
        result = self.mod.populate_panel(MagicMock(), q, 'en')
        self.assertEqual(result['refType'], 'roads')
        self.assertIn('Boulevard', result['refName'])
        self.assertIn('Didouche Mourad', result['refName'])

    def test_with_organization(self):
        q = self._make_panel_query(
            road_id=None, organization_id='org-1', subdivision_id=None
        )
        result = self.mod.populate_panel(MagicMock(), q, 'en')
        self.assertEqual(result['refType'], 'facilities')
        self.assertIn('Hospital', result['refName'])
        self.assertIn('CHU', result['refName'])

    def test_with_subdivision(self):
        q = self._make_panel_query(
            road_id=None, organization_id=None, subdivision_id='sub-1'
        )
        result = self.mod.populate_panel(MagicMock(), q, 'en')
        self.assertEqual(result['refType'], 'subdivisions')
        self.assertEqual(result['refName'], 'Cite Nord')

    def test_no_ref(self):
        q = self._make_panel_query()
        result = self.mod.populate_panel(MagicMock(), q, 'en')
        self.assertNotIn('refType', result)
        self.assertNotIn('refName', result)


class TestPopulateDispatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_dispatch_has_all_keys(self):
        expected = {
            'roads',
            'facilities',
            'subdivisions',
            'zones',
            'numbering',
            'panels',
        }
        self.assertEqual(set(self.mod.POPULATE_DISPATCH.keys()), expected)

    def test_dispatch_values_are_callables(self):
        for key, fn in self.mod.POPULATE_DISPATCH.items():
            self.assertTrue(callable(fn), f'{key} is not callable')

    def test_dispatch_maps_correct_functions(self):
        self.assertIs(self.mod.POPULATE_DISPATCH['roads'], self.mod.populate_road)
        self.assertIs(
            self.mod.POPULATE_DISPATCH['facilities'], self.mod.populate_facility
        )
        self.assertIs(
            self.mod.POPULATE_DISPATCH['subdivisions'], self.mod.populate_subdivision
        )
        self.assertIs(self.mod.POPULATE_DISPATCH['zones'], self.mod.populate_zone)
        self.assertIs(
            self.mod.POPULATE_DISPATCH['numbering'], self.mod.populate_numbering
        )
        self.assertIs(self.mod.POPULATE_DISPATCH['panels'], self.mod.populate_panel)


class TestNotifyHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_notify_success(self):
        with patch.object(self.mod, 'QMessageBox') as mock_qmb, \
             patch.object(self.mod, 'get_string', side_effect=lambda s, loc=None: s) as _gs:
            dialog = _make_dialog()
            self.mod._notify_success(dialog, 'update ok')
            mock_qmb.information.assert_called_once()
            args = mock_qmb.information.call_args[0]
            self.assertEqual(args[0], dialog)
            self.assertIn('Success', args[1])
            self.assertIn('update ok', args[2])

    def test_notify_failure(self):
        with patch.object(self.mod, 'QMessageBox') as mock_qmb, \
             patch.object(self.mod, 'get_string', side_effect=lambda s, loc=None: s) as _gs:
            dialog = _make_dialog()
            exc = RuntimeError('db exploded')
            self.mod._notify_failure(dialog, 'update failed', exc)
            mock_qmb.critical.assert_called_once()
            args = mock_qmb.critical.call_args[0]
            self.assertEqual(args[0], dialog)
            self.assertIn('Error', args[1])
            self.assertIn('update failed', args[2])


class TestFinishUpdate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_calls_refresh_and_close(self):
        with patch.object(self.mod, 'refresh_all_layers') as mock_refresh:
            dialog = _make_dialog()
            self.mod._finish_update(dialog)
            mock_refresh.assert_called_once_with(dialog.iface)
            dialog.close.assert_called_once()


class TestData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_returns_current_form_data(self):
        dialog = _make_dialog()
        dialog._current_form_data = {'name': 'Test', 'type': 'Road'}
        self.assertIs(self.mod._data(dialog), dialog._current_form_data)

    def test_returns_empty_dict(self):
        dialog = _make_dialog()
        dialog._current_form_data = {}
        self.assertEqual(self.mod._data(dialog), {})


class TestUpdateEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_success_path(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            model_class = MagicMock()
            dialog = _make_dialog()
            self.mod._update_entity(dialog, model_class, 'ok', 'fail', name='foo')
            model_class.update.assert_called_once_with(
                mock_sess.return_value,
                record_id='rec-1',
                name='foo',
            )
            mock_ns.assert_called_once_with(dialog, 'ok')
            mock_fu.assert_called_once_with(dialog)
            mock_sess.return_value.close.assert_called_once()

    def test_value_error_path(self):
        with patch.object(self.mod, '_notify_failure') as mock_nf, \
             patch.object(self.mod, 'get_session') as mock_sess:
            model_class = MagicMock()
            model_class.update.side_effect = ValueError('bad input')
            dialog = _make_dialog()
            self.mod._update_entity(dialog, model_class, 'ok', 'fail', name='x')
            mock_nf.assert_called_once()
            self.assertEqual(mock_nf.call_args[0][1], 'fail')
            mock_sess.return_value.close.assert_called_once()

    def test_sqlalchemy_error_path(self):
        from sqlalchemy.exc import SQLAlchemyError
        with patch.object(self.mod, '_notify_failure') as mock_nf, \
             patch.object(self.mod, 'get_session') as mock_sess:
            model_class = MagicMock()
            model_class.update.side_effect = SQLAlchemyError('conn lost')
            dialog = _make_dialog()
            self.mod._update_entity(dialog, model_class, 'ok', 'fail', name='x')
            mock_nf.assert_called_once()
            mock_sess.return_value.close.assert_called_once()


class TestUpdateRoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_calls_update_entity(self):
        with patch.object(self.mod, '_update_entity') as mock_ue:
            dialog = _make_dialog()
            dialog._current_form_data = {'name': '  Test Road  ', 'type': 'Avenue'}
            self.mod.update_road(dialog)
            mock_ue.assert_called_once()
            call_kwargs = mock_ue.call_args
            self.assertIs(call_kwargs[0][0], dialog)
            from plans_adressage.app.orders.models import Road

            self.assertIs(call_kwargs[0][1], Road)
            self.assertIn('updated successfully', call_kwargs[0][2])
            self.assertIn('Cannot update', call_kwargs[0][3])
            self.assertEqual(call_kwargs[1]['name'], 'Test Road')
            self.assertEqual(call_kwargs[1]['type'], 'Avenue')


class TestUpdateOrganization(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_calls_update_entity(self):
        with patch.object(self.mod, '_update_entity') as mock_ue:
            dialog = _make_dialog()
            dialog._current_form_data = {
                'name': 'Hospital',
                'type': 'Medical',
                'category': 'health',
            }
            self.mod.update_organization(dialog)
            mock_ue.assert_called_once()
            args = mock_ue.call_args[0]
            from plans_adressage.app.orders.models import Organization

            self.assertIs(args[1], Organization)
            self.assertEqual(mock_ue.call_args[1]['name'], 'Hospital')
            self.assertEqual(mock_ue.call_args[1]['type'], 'Medical')
            self.assertEqual(mock_ue.call_args[1]['category'], 'health')


class TestUpdateSubdivision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_calls_update_entity(self):
        with patch.object(self.mod, '_update_entity') as mock_ue:
            dialog = _make_dialog()
            dialog._current_form_data = {'name': 'Cite 500', 'type': 'Residential'}
            self.mod.update_subdivision(dialog)
            mock_ue.assert_called_once()
            from plans_adressage.app.orders.models import Subdivision

            self.assertIs(mock_ue.call_args[0][1], Subdivision)
            self.assertEqual(mock_ue.call_args[1]['name'], 'Cite 500')
            self.assertEqual(mock_ue.call_args[1]['type'], 'Residential')


class TestUpdateZone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_calls_update_entity(self):
        with patch.object(self.mod, '_update_entity') as mock_ue:
            dialog = _make_dialog()
            dialog._current_form_data = {'name': 'Zone A', 'type': 'Industrial'}
            self.mod.update_zone(dialog)
            mock_ue.assert_called_once()
            from plans_adressage.app.orders.models import Zone

            self.assertIs(mock_ue.call_args[0][1], Zone)
            self.assertEqual(mock_ue.call_args[1]['name'], 'Zone A')
            self.assertEqual(mock_ue.call_args[1]['type'], 'Industrial')


class TestUpdatePanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    def setUp(self):
        from plans_adressage.app.orders.models import PanelSign

        PanelSign.update.reset_mock()
        PanelSign.update.side_effect = None

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._lvp.stop()

    def test_ref_facilities(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='org-1', _ref_layer='facilities')
            dialog._current_form_data = {'mountStatus': 'mounted'}
            self.mod.update_panel(dialog)
            from plans_adressage.app.orders.models import PanelSign

            PanelSign.update.assert_called_once_with(
                mock_sess.return_value,
                record_id='rec-1',
                status='mounted',
                organization_id='org-1',
                road_id=None,
                subdivision_id=None,
            )
            mock_ns.assert_called_once()
            mock_fu.assert_called_once()

    def test_ref_roads(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='road-1', _ref_layer='roads')
            dialog._current_form_data = {'mountStatus': 'planned'}
            self.mod.update_panel(dialog)
            from plans_adressage.app.orders.models import PanelSign

            PanelSign.update.assert_called_once_with(
                mock_sess.return_value,
                record_id='rec-1',
                status='planned',
                road_id='road-1',
                subdivision_id=None,
                organization_id=None,
            )

    def test_ref_subdivisions(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='sub-1', _ref_layer='subdivisions')
            dialog._current_form_data = {'mountStatus': 'to_fix'}
            self.mod.update_panel(dialog)
            from plans_adressage.app.orders.models import PanelSign

            PanelSign.update.assert_called_once_with(
                mock_sess.return_value,
                record_id='rec-1',
                status='to_fix',
                subdivision_id='sub-1',
                road_id=None,
                organization_id=None,
            )

    def test_no_ref_id(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id=None, _ref_layer=None)
            dialog._current_form_data = {'mountStatus': 'old'}
            self.mod.update_panel(dialog)
            from plans_adressage.app.orders.models import PanelSign

            PanelSign.update.assert_called_once_with(
                mock_sess.return_value,
                record_id='rec-1',
                status='old',
            )

    def test_error_path(self):
        from sqlalchemy.exc import SQLAlchemyError
        with patch.object(self.mod, '_notify_failure') as mock_nf, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='org-1', _ref_layer='facilities')
            dialog._current_form_data = {'mountStatus': 'x'}
            from plans_adressage.app.orders.models import PanelSign

            PanelSign.update.side_effect = SQLAlchemyError('fail')
            self.mod.update_panel(dialog)
            mock_nf.assert_called_once()
            self.assertIn('Cannot update panel', mock_nf.call_args[0])


class TestUpdateNumbering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls._lvp, cls._vtp = _patch_constants(cls.mod)
        cls._lvp.start()
        cls._vtp.start()

    def setUp(self):
        from plans_adressage.app.orders.models import Numbering

        Numbering.update.reset_mock()
        Numbering.update.side_effect = None

    @classmethod
    def tearDownClass(cls):
        cls._vtp.stop()
        cls._vtp.stop()

    def test_ref_facilities(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='org-1', _ref_layer='facilities')
            dialog._current_form_data = {
                'number': '42',
                'repetition': 'bis',
                'state': 'booked',
                'activityCat': 'residential',
                'activityType': 'house',
            }
            self.mod.update_numbering(dialog)
            from plans_adressage.app.orders.models import Numbering

            Numbering.update.assert_called_once()
            call_kw = Numbering.update.call_args[1]
            self.assertEqual(call_kw['organization_id'], 'org-1')
            self.assertIsNone(call_kw['road_id'])
            self.assertIsNone(call_kw['subdivision_id'])
            self.assertEqual(call_kw['value'], '42')
            self.assertEqual(call_kw['repetition'], 'bis')
            self.assertEqual(call_kw['state'], 'booked')
            self.assertEqual(call_kw['activity_cat'], 'residential')
            self.assertEqual(call_kw['activity_type'], 'house')

    def test_ref_roads(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='road-1', _ref_layer='roads')
            dialog._current_form_data = {
                'number': '7',
                'repetition': '',
                'state': 'planned',
                'activityCat': '',
                'activityType': '',
            }
            self.mod.update_numbering(dialog)
            from plans_adressage.app.orders.models import Numbering

            call_kw = Numbering.update.call_args[1]
            self.assertEqual(call_kw['road_id'], 'road-1')
            self.assertIsNone(call_kw['subdivision_id'])
            self.assertIsNone(call_kw['organization_id'])

    def test_ref_subdivisions(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='sub-1', _ref_layer='subdivisions')
            dialog._current_form_data = {
                'number': '10',
                'repetition': '',
                'state': '',
                'activityCat': '',
                'activityType': '',
            }
            self.mod.update_numbering(dialog)
            from plans_adressage.app.orders.models import Numbering

            call_kw = Numbering.update.call_args[1]
            self.assertEqual(call_kw['subdivision_id'], 'sub-1')
            self.assertIsNone(call_kw['road_id'])
            self.assertIsNone(call_kw['organization_id'])

    def test_no_ref(self):
        with patch.object(self.mod, '_finish_update') as mock_fu, \
             patch.object(self.mod, '_notify_success') as mock_ns, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id=None, _ref_layer=None)
            dialog._current_form_data = {
                'number': '',
                'repetition': '',
                'state': '',
                'activityCat': '',
                'activityType': '',
            }
            self.mod.update_numbering(dialog)
            from plans_adressage.app.orders.models import Numbering

            call_kw = Numbering.update.call_args[1]
            self.assertIsNone(call_kw['road_id'])
            self.assertIsNone(call_kw['subdivision_id'])
            self.assertIsNone(call_kw['organization_id'])

    def test_error_path(self):
        with patch.object(self.mod, '_notify_failure') as mock_nf, \
             patch.object(self.mod, 'get_session') as mock_sess:
            dialog = _make_dialog(_ref_id='org-1', _ref_layer='facilities')
            dialog._current_form_data = {
                'number': '1',
                'repetition': '',
                'state': '',
                'activityCat': '',
                'activityType': '',
            }
            from plans_adressage.app.orders.models import Numbering

            Numbering.update.side_effect = ValueError('bad value')
            self.mod.update_numbering(dialog)
            mock_nf.assert_called_once()
            self.assertIn('Cannot update numbering', mock_nf.call_args[0])


if __name__ == '__main__':
    unittest.main()
