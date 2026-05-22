"""Test that plugin resources exist on disk."""
import os
import unittest


class ResourcesTest(unittest.TestCase):
    """Verify plugin resources exist on disk."""

    def test_icon_exists(self):
        """The plugin icon should exist at the expected path."""
        path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icon.png')
        self.assertTrue(os.path.isfile(os.path.abspath(path)),
                        'resources/icon.png should exist')


if __name__ == "__main__":
    unittest.main()
