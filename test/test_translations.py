"""Translations Test.

Verifies the plugin's i18n assets: the Qt linguist catalogs shipped in
``i18n/`` and the JSON lookup tables used at runtime by
``scripts.widget_texts``.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 3 of the License, or
     (at your option) any later version.

"""

import json
import os
import unittest
import xml.etree.ElementTree as ET

PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
I18N_DIR = os.path.join(PLUGIN_ROOT, 'i18n')
DATA_DIR = os.path.join(PLUGIN_ROOT, 'template_data')

SUPPORTED_LOCALES = ('ar', 'en', 'fr')


class TranslationCatalogTest(unittest.TestCase):
    """Test that the Qt linguist catalogs are present and well-formed."""

    def test_catalogs_exist(self):
        """Each supported locale ships a .ts catalog."""
        for locale in SUPPORTED_LOCALES:
            path = os.path.join(I18N_DIR, f'CAM_{locale}.ts')
            self.assertTrue(os.path.isfile(path), f'{path} should exist')

    def test_catalogs_are_valid_ts(self):
        """Each catalog parses as TS XML and contains translated messages."""
        for locale in SUPPORTED_LOCALES:
            path = os.path.join(I18N_DIR, f'CAM_{locale}.ts')
            root = ET.parse(path).getroot()
            messages = root.findall('.//message')
            self.assertTrue(messages, f'{path} should contain messages')
            translated = [
                m
                for m in messages
                if m.findtext('translation') not in (None, '', 'unfinished')
            ]
            self.assertTrue(translated, f'{path} should contain finished translations')


class StringLookupTest(unittest.TestCase):
    """Test the runtime string lookup used by the UI."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(DATA_DIR, 'strings.json'), encoding='utf-8') as f:
            cls.strings = json.load(f)

    def test_strings_json_exists_with_entries(self):
        """strings.json exists and defines source strings."""
        self.assertTrue(self.strings, 'strings.json should define strings')

    def test_every_entry_covers_all_locales(self):
        """Every entry provides a translation for each supported locale."""
        for source, data in self.strings.items():
            self.assertIsInstance(
                data, dict, f'entry for {source!r} should map locales'
            )
            for locale in SUPPORTED_LOCALES:
                self.assertIn(locale, data, f'{source!r} missing {locale} translation')
                self.assertTrue(data[locale], f'{source!r} has empty {locale}')

    def test_lookup_resolves_known_string(self):
        """get_string resolves a known source string for each locale."""
        from scripts.widget_texts import clear_i18n_cache, get_string

        clear_i18n_cache()
        source, expected = next(iter(self.strings.items()))
        for locale in SUPPORTED_LOCALES:
            self.assertEqual(get_string(source, locale), expected[locale])

    def test_lookup_falls_back_to_source(self):
        """get_string returns the source text for unknown keys."""
        from scripts.widget_texts import clear_i18n_cache, get_string

        clear_i18n_cache()
        self.assertEqual(get_string('No such key', 'fr'), 'No such key')


if __name__ == '__main__':
    unittest.main()
