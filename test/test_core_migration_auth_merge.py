"""Tests for app.core.migration._merge_auth_users."""

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.core.migration import _merge_auth_users


class TestMergeAuthUsers(unittest.TestCase):
    def test_no_auth_path(self):
        _merge_auth_users('/tmp/new.db', None)

    def test_auth_path_not_exists(self):
        _merge_auth_users('/tmp/new.db', '/nonexistent/auth.sqlite')

    def test_auth_db_no_user_table(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            auth_path = f.name
        try:
            conn = sqlite3.connect(auth_path)
            conn.execute('CREATE TABLE dummy (id TEXT)')
            conn.commit()
            conn.close()
            _merge_auth_users('/tmp/new.db', auth_path)
        finally:
            os.unlink(auth_path)

    def test_auth_db_empty_user_table(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            auth_path = f.name
        try:
            conn = sqlite3.connect(auth_path)
            conn.execute('CREATE TABLE user (id TEXT, username TEXT)')
            conn.commit()
            conn.close()
            _merge_auth_users('/tmp/new.db', auth_path)
        finally:
            os.unlink(auth_path)

    def test_merge_users_into_target(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.execute("INSERT INTO user VALUES ('u2', 'bob')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.execute("INSERT INTO user VALUES ('u1', 'alice')")
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT * FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], ('u1', 'alice'))
            self.assertEqual(rows[1], ('u2', 'bob'))
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_all_users_new_target(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.execute("INSERT INTO user VALUES ('u2', 'bob')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT, username TEXT)')
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT * FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(len(rows), 2)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_operational_error_on_insert_is_handled(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT, username TEXT)')
            tc.commit()
            tc.close()

            original_connect = sqlite3.connect
            target_mock = MagicMock()
            target_mock.total_changes = 0

            def _raise_on_insert(sql, *a, **kw):
                if sql.lstrip().upper().startswith('INSERT'):
                    raise sqlite3.OperationalError('constraint')
                cursor = MagicMock()
                cursor.fetchall.return_value = []
                return cursor

            target_mock.execute.side_effect = _raise_on_insert

            def _connect(path, *a, **kw):
                if path == target_path:
                    return target_mock
                return original_connect(path, *a, **kw)

            with (
                patch('app.core.migration.sqlite3.connect', side_effect=_connect),
                self.assertLogs('app.core.migration', level='WARNING'),
            ):
                _merge_auth_users(target_path, auth_path)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_counts_only_inserted_users(self):
        """INSERT OR IGNORE rows that are ignored must not count as merged."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.execute("INSERT INTO user VALUES ('u2', 'bob')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            # u1 already exists in the target, so its INSERT OR IGNORE is a no-op.
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.execute("INSERT INTO user VALUES ('u1', 'alice')")
            tc.commit()
            tc.close()

            with self.assertLogs('app.core.migration', level='INFO') as cm:
                _merge_auth_users(target_path, auth_path)
            self.assertTrue(any('Merged 1 user(s)' in m for m in cm.output))
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_malicious_column_name_is_rejected(self):
        """Columns from an untrusted auth file must not reach raw SQL."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            # A crafted column name that breaks out of the double-quoted
            # identifier when interpolated.  Built from parts so source
            # formatters cannot alter the payload; the doubled "" inside
            # the DDL identifier yields a single '"' in the stored name.
            d = chr(34)  # double quote
            q = chr(39)  # single quote
            hostile_col = f'x{d}) VALUES({q}p{q}); DROP TABLE user;--'
            ac.execute(
                f'CREATE TABLE user ({d}id{d} TEXT, {d}{d}{hostile_col}{d} TEXT)'
            )
            ac.execute(f'INSERT INTO user VALUES ({q}u1{q}, {q}evil{q})')
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.commit()
            tc.close()

            with self.assertLogs('app.core.migration', level='WARNING'):
                _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            tables = {
                r[0]
                for r in tc.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            usernames = [
                row[1] if len(row) > 1 else None
                for row in tc.execute('SELECT * FROM user').fetchall()
            ]
            tc.close()
            # The hostile column must not have been interpolated: the user
            # table was not dropped and no rogue payload was stored.
            self.assertIn('user', tables)
            self.assertNotIn('evil', usernames)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_unknown_columns_are_skipped(self):
        """Columns absent from the target schema are ignored, not inserted."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT, legacy_col TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice', 'junk')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT id, username FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(rows, [('u1', 'alice')])
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)


if __name__ == '__main__':
    unittest.main()
