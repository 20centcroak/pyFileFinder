import unittest
import os
from unittest.mock import MagicMock

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

    def test_folder_go_in_folder(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'folder.*',
            'goIntoFoundFolder': True,
            'stopWhenFound': False
        }
        folders = Finder(settings).findFolders()
        self.assertTrue(folders)
        self.assertEqual(len(folders),3)
        result = [os.path.basename(folder) for folder in folders]
        self.assertCountEqual(result,['folder1', 'folder2', 'folder3'])

    def test_folder_dont_go_in_folder(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'folder.*',
            'goIntoFoundFolder': False,
            'stopWhenFound': False
        }
        folders = Finder(settings).findFolders()
        self.assertTrue(folders)
        self.assertEqual(len(folders),2)
        result = [os.path.basename(folder) for folder in folders]
        self.assertCountEqual(result,['folder1', 'folder3'])


    def test_file_case_sensitive(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'file.*2',
            'caseSensitive': True,
            'depth':-1,
            'stopWhenFound': False
        }
        files = Finder(settings).findFiles()
        self.assertTrue(files)
        self.assertEqual(len(files),2)
        result = [os.path.basename(file) for file in files]
        self.assertCountEqual(result,['file2_2.txt', 'file1_2.txt'])

    def test_file(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'file.*2',
            'caseSensitive': False,
            'depth':-1,
            'stopWhenFound': False
        }
        files = Finder(settings).findFiles()
        self.assertTrue(files)
        self.assertEqual(len(files),3)
        result = [os.path.basename(file) for file in files]
        self.assertCountEqual(result,['fiLe2_1.txt', 'file2_2.txt', 'file1_2.txt'])

    def test_file_depth(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'file.*',
            'depth':1,
            'stopWhenFound': False
        }
        files = Finder(settings).findFiles()
        self.assertTrue(files)
        self.assertEqual(len(files),3)
        result = [os.path.basename(file) for file in files]
        self.assertCountEqual(result,['file1_1.txt', 'file1_2.txt', 'file3_1.txt'])

    def test_file_avoid_folder(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'file.*',
            'avoidFolders': ['folder3'],
            'depth':1,
            'stopWhenFound': False
        }
        files = Finder(settings).findFiles()
        self.assertTrue(files)
        self.assertEqual(len(files),2)
        result = [os.path.basename(file) for file in files]
        self.assertCountEqual(result,['file1_1.txt', 'file1_2.txt'])

    def test_zip(self):
        settings = {
            'parent':'tests/unit/resources/archive.zip',
            'regex': r'archive.*',
            'stopWhenFound': False
        }
        files = Finder(settings).findFilesInZip()
        self.assertTrue(files)
        self.assertEqual(len(files),1)
        result = [os.path.basename(file) for file in files]
        self.assertCountEqual(result,['archive.txt'])

    def test_ftp_all_files(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'.*',
            'caseSensitive': False,
            'stopWhenFound': False,
            'depth': 0
        }
        finder = Finder(settings)

        return_value = [['d', '.'], ['drwxr-xr-x', 'notes', 'folder1'], ['-rw-r--r--', 'notes', 'file1'], ['-rw-r--r--', 'notes', 'file2']]

        finder._getFtpFileInfo = MagicMock(return_value=return_value)

        files = finder.findFilesInFtp()
        result = [os.path.basename(file) for file in files]
        expected =  ['file1','file2']
        self.assertCountEqual(result,expected)

    def test_ftp_files_stop_when_found(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'.*',
            'caseSensitive': False,
            'depth': 0
        }
        finder = Finder(settings)

        return_value = [['d', '.'], ['drwxr-xr-x', 'notes', 'folder1'], ['-rw-r--r--', 'notes', 'file1'], ['-rw-r--r--', 'notes', 'file2']]

        finder._getFtpFileInfo = MagicMock(return_value=return_value)

        files = finder.findFilesInFtp()
        result = [os.path.basename(file) for file in files]
        expected =  ['file1']
        self.assertCountEqual(result,expected)

    def test_ftp_folder(self):
        settings = {
            'parent':'tests/unit/resources',
            'regex': r'.*',
            'caseSensitive': False,
            'depth': 0
        }
        finder = Finder(settings)

        return_value = [['d', '.'], ['drwxr-xr-x', 'notes', 'folder1'], ['-rw-r--r--', 'notes', 'file1'], ['-rw-r--r--', 'notes', 'file2']]

        finder._getFtpFileInfo = MagicMock(return_value=return_value)

        files = finder.findFoldersInFtp()
        result = [os.path.basename(file) for file in files]
        expected =  ['folder1']
        self.assertCountEqual(result,expected)