import unittest

from pyFileFinder import Finder

class TestFinder(unittest.TestCase):

    def test_folder(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'^F.*3',
            'caseSensitive': False
        }
        folders = Finder(settings).findFolders()
        self.assertTrue(folders)
        self.assertEqual(len(folders),1)
        self.assertEqual(folders[0],'folder3')