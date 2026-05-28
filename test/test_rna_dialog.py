"""Test that the main dialog module exists."""
import os
import unittest


class MainDialogImportTest(unittest.TestCase):
    """Verify the main dialog file exists."""

    def test_module_file_exists(self):
        """gui/main_dialog.py should exist."""
        path = os.path.join(
            os.path.dirname(__file__), '..', 'gui', 'main_dialog.py')
        self.assertTrue(os.path.isfile(os.path.abspath(path)),
                        'gui/main_dialog.py should exist')


if __name__ == "__main__":
    unittest.main()
