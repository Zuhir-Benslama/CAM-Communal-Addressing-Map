"""Tests for app.shared.odt_report (programmatic ODT generation)."""

import unittest
import zipfile
import xml.dom.minidom
from pathlib import Path

from app.shared import odt_report

_SAMPLE = {
    'date': '2026/08/27',
    'wilaya': '16',
    'commune': 'Alger Centre',
    'zones': 3,
    'roads': 12,
    'subs': 5,
    'orgs': 8,
    'num_total': 100,
    'pan_total': 40,
    'prog': 60,
    'right': 30,
    'wrong': 5,
    'booked': 5,
    'pan_city1': 10,
    'pan_org1': 5,
    'pan_road1': 5,
    'pan_city0': 8,
    'pan_org0': 4,
    'pan_road0': 3,
    'pan_city2': 2,
    'pan_org2': 1,
    'pan_road2': 1,
    'pan_city3': 1,
    'pan_org3': 0,
    'pan_road3': 1,
    'pan_std': 30,
    'creation_date': '2026-08-27',
}


class TestOdtReport(unittest.TestCase):
    def setUp(self):
        self.out = Path(__file__).parent / '__odt_report_test.odt'

    def tearDown(self):
        self.out.unlink(missing_ok=True)

    def test_build_returns_valid_package(self):
        data = odt_report.build_statistical_report(_SAMPLE, self.out)
        self.assertTrue(isinstance(data, bytes))
        self.assertGreater(len(data), 0)
        self.assertTrue(zipfile.is_zipfile(self.out))

    def test_mimetype_stored_first_uncompressed(self):
        odt_report.build_statistical_report(_SAMPLE, self.out)
        with zipfile.ZipFile(self.out) as zf:
            self.assertEqual(zf.namelist()[0], 'mimetype')
            self.assertEqual(zf.getinfo('mimetype').compress_type, zipfile.ZIP_STORED)
            self.assertEqual(
                zf.read('mimetype').decode(),
                'application/vnd.oasis.opendocument.text',
            )

    def test_required_members_present(self):
        odt_report.build_statistical_report(_SAMPLE, self.out)
        with zipfile.ZipFile(self.out) as zf:
            for member in (
                'META-INF/manifest.xml',
                'content.xml',
                'styles.xml',
                'meta.xml',
            ):
                self.assertIn(member, zf.namelist())

    def test_xml_parts_well_formed(self):
        odt_report.build_statistical_report(_SAMPLE, self.out)
        with zipfile.ZipFile(self.out) as zf:
            for member in ('content.xml', 'styles.xml', 'meta.xml'):
                xml.dom.minidom.parseString(zf.read(member))

    def test_content_contains_report_values(self):
        odt_report.build_statistical_report(_SAMPLE, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml').decode('utf-8')
        self.assertIn('Alger Centre', content)
        self.assertIn('100', content)
        # numeric placeholders are rendered inline, not as unresolved tokens
        self.assertNotIn('data.get(', content)

    def test_escape_special_characters(self):
        data = dict(_SAMPLE, commune='<Oran & Tests>')
        odt_report.build_statistical_report(data, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml')
        xml.dom.minidom.parseString(content)  # must remain well-formed

    def test_default_title_used_for_empty(self):
        data = {k: v for k, v in _SAMPLE.items() if k not in ('date',)}
        data['creation_date'] = '2026-08-27'
        odt_report.build_statistical_report(data, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml').decode('utf-8')
        self.assertIn('التقرير الإحصائي', content)

    def test_localised_labels_by_locale(self):
        data = dict(_SAMPLE, locale='fr')
        data['creation_date'] = '2026-08-27'
        odt_report.build_statistical_report(data, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml').decode('utf-8')
        self.assertIn('Rapport Statistique', content)
        self.assertIn('Statistiques Générales', content)
        self.assertIn('Total des numéros', content)

    def test_localised_english_labels(self):
        data = dict(_SAMPLE, locale='en')
        data['creation_date'] = '2026-08-27'
        odt_report.build_statistical_report(data, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml').decode('utf-8')
        self.assertIn('Statistical Report', content)
        self.assertIn('Total panels', content)
        self.assertIn('Generated on', content)

    def test_invalid_locale_falls_back_to_arabic(self):
        data = dict(_SAMPLE, locale='xx')
        data['creation_date'] = '2026-08-27'
        odt_report.build_statistical_report(data, self.out)
        with zipfile.ZipFile(self.out) as zf:
            content = zf.read('content.xml').decode('utf-8')
        self.assertIn('التقرير الإحصائي', content)

    def test_styled_output_uses_accent_colours(self):
        odt_report.build_statistical_report(_SAMPLE, self.out)
        with zipfile.ZipFile(self.out) as zf:
            styles = zf.read('styles.xml').decode('utf-8')
        self.assertIn('#1f4e79', styles)
        self.assertIn('#ddebf7', styles)
        self.assertIn('TitleRow', styles)
        self.assertIn('SectionHeader', styles)


if __name__ == '__main__':
    unittest.main()
