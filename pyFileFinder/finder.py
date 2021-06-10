"""
This is an objected-oriented file finder module.

It looks for files and folders in os directories, ftp location or in zip archives.
Search is based on regex.

Many options are available to stop or continue search when a file or folder is found.

"""
import logging
import os
import re
from typing import Generator
from zipfile import ZipFile
from pathlib import Path

class Finder():
    """
    The Finder class offers convenient functions to search files and folders based on regex.
    """

    def __init__(self, settings=None):
        """
        builds the class according to the settings definition.
        Parameters
        ----------
        settings : object that may contain the following key and values

        - parent: gives the root directory into which files or folders should be searched. 
        If not set, the current folder (folder from which the script is launched) will be used

        - regex: regular expression used to check if a file or folder is part of the search. 
        It could be a single expression or a list of expressions
        Default value is '.*' : it looks for any file or folder. 
        If for example we want to list all files and folders of the parent folder, this default value may be used in association with depth=1

        - depth: depth of research. If set to 0, then files and folders are only searched in the parent folder. 
        If set to n (n as an integer), then search goes up to the n-th subdirectory. 
        Default value is -1, which means that search doesn't stop while there is no more subfolder.

        - stopWhenFound: as soon as a file or folder complies with the regex, the search is topped and the found file or folder is returned 
        (in an array) to satisfy the more generic research. Default value is True.

        - goIntoFoundFolder: When False, if a folder is searched and found, does not look inside for subfolders that comply with regex. 
        This is different of stopWhenFound: it may find multiple folders but does not look into a found folder. Default value is False.

        - avoidFolders: array of folder names to exclude in the search. Does not either return these folders or look into. 
        Default value is empty.

        - caseSensitive: if true, the regex is case sensitive. Default value is True.

        - ftpConnection: ftp connection to be used when looking in a ftp location. 
        This connection is returned when calling ftplib FTP(host, user, pwd)

        """
        self.parent = Path(os.getcwd())
        self.regex = ['.*']
        self.depth = -1
        self.stopWhenFound = True
        self.goIntoFoundFolder = False
        self.avoidFolders = []
        self.caseSensitive = True
        self.ftpConnection = None
        self._setProperties(settings)

        # if self.parent != '/':
        #     self.parent = Path(self.parent).resolve()
        #     if not self.parent.exists():
        #         raise FileNotFoundError('parent folder {} not found'.format(self.parent))


    def getFile(self, parent:os.PathLike, regex: str)->Path:
        """
        basic regex file search - case insensitive and only in given parent folder - return first found file matching the regex.

        Parameters:
        ----------
        parent: PathLike of parent folder where to search for file
        regex: regex that file should match

        Returns:
        -------
        Path of first found file matching the regex - None, if no file is found
        """
        self.parent = Path(parent)
        self.depth = 0
        self.caseSensitive = False
        self.regex = regex
        files = self.findFiles()
        try:
            return next(files)
        except StopIteration:
            return None

    def findFolders(self)->Generator:
        """
        find folders in the os directory according to the settings defined when building the Finder object.

        Returns:
        -------
        iterator which yields found folders
        """
        logging.debug('looking for folders {} in {}'.format(self.regex, self.parent))
        return self._findAllFolders(self._walkFile)

    def matchFolders(self)->tuple:
        """
        find folders according to the settings defined when building the Finder object; 
        If every regex returns a result, then match is true

        Returns:
        -------
        tuple of (match, founds, missed) where:
            - match is true if each regex returns a result, false otherwise
            - founds = found folder Paths
            - missed = list of regex that do not return a result (failures)
        """
        logging.debug('looking for folders {} in {}'.format(self.regex, self.parent))
        founds = []
        missed = []
        match = True

        all_regex = self.regex.copy()
        for reg in all_regex:
            found = False
            self.regex = [reg]
            folders = self._findAllFolders(self._walkFile)
            for folder in folders:
                found = True
                founds.append(folder)
            match = match and found
            if not found:
                missed.append(reg)
        return (match, founds, missed)

    def findFoldersInFtp(self)->Generator:
        """
        find folders in the ftp location according to the settings defined when building the Finder object

        Returns:
        -------
        iterator which yields found folders
        """
        logging.debug('looking for folders {} in ftp {}'.format(self.regex, self.parent))
        return self._findAllFolders(self._walkFTP, True)

    def findFiles(self)->Generator:
        """
        find files in os directory according to the settings defined when building the Finder object

        Returns:
        -------
        iterator which yields found files
        """
        logging.debug('looking for files {} in {}'.format(self.regex, self.parent))
        return self._findAllFiles(self._walkFile)

    def matchFiles(self)->tuple:
        """
        find files in os directory according to the settings defined when building the Finder object; 
        If every regex returns a result, then match is true

        Returns:
        -------
        tuple of (match, founds, missed) where:
            - match is true if each regex returns a result, false otherwise
            - founds = found file Paths
            - missed = list of regex that do not return a result (failures)
        """
        logging.debug('looking for files {} in {}'.format(self.regex, self.parent))
        founds = []
        missed = []
        match = True

        all_regex = self.regex.copy()
        for reg in all_regex:
            logging.debug('test regex %s', reg)
            found = False
            self.regex = [reg]
            files = self._findAllFiles(self._walkFile)
            for file in files:
                logging.debug('found %s', file)
                found = True
                founds.append(file)
            match = match and found
            logging.debug('match %s', match)
            if not found:
                missed.append(reg)
        return (match, founds, missed)

    def findFilesInFtp(self)->Generator:
        """
        find files in ftp location according to the settings defined when building the Finder object
        
        Returns:
        -------
        iterator which yields found files
        """
        logging.debug('looking for files {} in ftp {}'.format(self.regex, self.parent))
        return self._findAllFiles(self._walkFTP, True)

    def findFilesInZip(self)->Generator:
        """
        find files in a zip archive according to the settings defined when building the Finder object.
        In this case the "parent" setting should be the zip path
        
        Returns:
        -------
        iterator which yields found files
        """
        logging.debug('looking for files {} in zip {}'.format(self.regex, self.parent))
        return self._findAllFiles(self._walkZip)

    def _setProperties(self, settings: dict):
        if not settings:
            return
        for key in settings:
            if hasattr(self, key):
                setattr(self, key, settings[key])
            else:
                raise KeyError('{} is not a recognised settings')
        if type(self.regex) is not list:
            self.regex = [self.regex]

    def _findAllFiles(self, callback, isftp = False):
        for regex in self.regex:
            files = self._findFiles(callback, regex, isftp)
            for file in files:
                yield file

    def _findFiles(self, callback, regex, isftp = False):
        if not isftp:
            self.parent = Path(self.parent).resolve()
            if not self.parent.exists():
                raise FileNotFoundError('parent folder not found')
        flags = 0 if self.caseSensitive else re.IGNORECASE
        compiled = re.compile(regex, flags)
        found = False
        for dirpath, subdirs, files in callback(self.parent):
            logging.debug('scanning {}'.format(dirpath))
            for filename in files:
                if compiled.search(filename):
                    found = True
                    if isftp:
                        yield dirpath + '/' + filename
                    else:
                        yield Path(dirpath)/filename
                if self.stopWhenFound and found:
                    return
            for avoidFolder in self.avoidFolders:
                if avoidFolder in subdirs:
                    subdirs.remove(avoidFolder)

    def _findAllFolders(self, callback, isftp=False):
        for regex in self.regex:
            folders = self._findFolders(callback, regex, isftp)
            for folder in folders:
                yield folder

    def _findFolders(self, callback, regex, isftp = False):
        if not isftp:
            self.parent = Path(self.parent).resolve()
            if not self.parent.exists():
                raise FileNotFoundError('parent folder not found')
        flags = 0 if self.caseSensitive else re.IGNORECASE
        compiled = re.compile(regex, flags)
        found = False
        
        for dirpath, subdirs, _ in callback(self.parent):
            logging.debug('processing folder {}'.format(dirpath))
            toberemoved = []
            for subdir in subdirs:
                if compiled.search(subdir):
                    found = True
                    toberemoved.append(subdir)
                    if isftp:
                        yield dirpath + '/' + subdir
                    else:
                        yield Path(dirpath)/subdir
            if not self.goIntoFoundFolder:
                for folder in toberemoved:
                    subdirs.remove(folder)
            if self.stopWhenFound and found:
                break
            for avoidFolder in self.avoidFolders:
                if avoidFolder in subdirs:
                    subdirs.remove(avoidFolder)

    def _walkFile(self, path):
        initial_depth = str(self.parent).count(os.path.sep)
        for root, dirs, files in os.walk(path):
            num_sep_this = root.count(os.path.sep)
            yield root, dirs, files
            if initial_depth + self.depth <= num_sep_this and self.depth > -1:
                del dirs[:]

    def _walkZip(self, path):
        """
        Walk through Zip archive
        """
        zipFile = ZipFile(path, 'r')
        itemsInZip = zipFile.namelist()
        dirs = []
        nondirs = []
        for item in itemsInZip:
            groups = item.split('/')
            num_sep_this = len(groups) - 2
            if self.depth < num_sep_this and self.depth > -1:
                continue
            if item.endswith('/'):
                dirs.append(groups[-2])
            else:
                nondirs.append(groups[-1])
        yield path, dirs, nondirs

    def _listdirFTP(self, _path):
        dirs = []
        nondirs = []
        file_list = self._getFtpFileInfo(_path)
        for info in file_list:
            ls_type, name = info[0], info[-1]
            if re.match(r'^\.+$', name):
                continue
            if ls_type.startswith('d'):
                dirs.append(name)
            else:
                nondirs.append(name)
        return dirs, nondirs

    def _getFtpFileInfo(self, _path):
        """
        return files and directory names within a path (directory)
        """
        file_list = []
        try:
            self.ftpConnection.cwd(_path)
        except Exception as exp:
            logging.error(exp.__str__(), _path)
            return []
        else:
            self.ftpConnection.retrlines(
                'LIST', lambda x: file_list.append(x.split()))
        return file_list

    def _walkFTP(self, path):
        """
        Walk through FTP server's directory tree, based on a BFS algorithm.
        """
        initial_depth = self.parent.count('/')
        dirs, nondirs = self._listdirFTP(path)
        num_sep_this = path.count('/')
        yield path, dirs, nondirs
        if initial_depth + self.depth <= num_sep_this and self.depth > -1:
            del dirs[:]
        for name in dirs:
            yield from self._walkFTP(path+'/'+name)
            self.ftpConnection.cwd('.')
