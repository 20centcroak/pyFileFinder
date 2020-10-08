# pyFileFinder
module to easily find files in system, zip archives or ftp servers using regex

# Finder Class

## What?
The Finder class offers convenient functions to search files and folders based on regex.

## How?

1. First build the class by calling
```python
finder = Finder(settings)
```

settings : dictionary that may contain the following key and values.  
Available keys are {"parent", "regex", "depth", "stopWhenFound", "goIntoFoundFolder", "avoidFolders", "caseSensitive", "ftpConnection"}

- parent: gives the root directory into which files or folders should be searched. 
If not set, the current folder (folder from which the script is launched) will be used
When looking into an archive (zip file), this setting should be the path to the zip archive.

- regex: regular expression used to check if a file or folder is part of the search.
It could be a regex expression or a list of regex expressions 
Default value is '.*' : it looks for any file or folder. 
Check your regex using [regex101](https://regex101.com/) for example
For example if we want to list all files and folders of the parent folder, this default value may be used in association with depth=1

- depth: depth of research. If set to 0, then files and folders are only searched in the parent folder. 
If set to n (n as an integer), then search goes up to the n-th subdirectory. 
Default value is -1, which means that search doesn't stop while there is no more subfolder.

- stopWhenFound: as soon as a search return results complying with the regex, the search is stopped and the found files or folders are returned. 
Note that, even if the iterative process is stopped, the result may contain many file or folders when multiple files inside a folder comply with the regex for example.  
Default value is True.

- goIntoFoundFolder: When False, if a folder is searched and found, does not look inside for subfolders that comply with regex. 
This different of stopWhenFound: it may find multiple folders but does not look into a found folder. Default value is False.

- avoidFolders: array of folder names to exclude in the search. Does not either return these folders or look into. 
Default value is empty.

- caseSensitive: if true, the regex is case sensitive. Default value is True.

- ftpConnection: ftp connection to be used when looking in a ftp location. 
This connection is returned when calling ftplib FTP(host, user, pwd)

2. Call one of the above functions:
```python
finder = Finder(settings)
finder.findFolders()
finder.matchFolders()
finder.findFolderInFtp()
finder.findFiles()
finder.matchFiles()
finder.findFilesInFtp()
finder.findFilesInZip()
```

matchFiles or matchFolders return a tuple (ok, result_of_search) where ok is True if each regex expression returns a result and result_of_search 
is identical of the result of findFiles (resp. findFolders)

## Examples

Note that unit tests cover the full use of Finder features, see them here: [test_finder.py](https://github.com/20centcroak/pyFileFinder/blob/main/tests/unit/test_finder.py)

### Example1
Suppose that, starting from C:\myFolder, you want to look for folders for which names contain "level". These folders shouldn't be far away from 3 subfolders of C:\myFolder. Then, for each of these folders, you want to find 1 zip archive for which name contains myarchive. Finally you want to search in these zip archives all xml files. Here is the way to proceed :
```python
from files.finder import Finder

if __name__ == "__main__":

    # step1: find folders
    settings = {'parent': 'C:/myFolder', 'regex': 'level',
                'depth': 3, 'stopWhenFound': False, 'goIntoFolder': False}
    folders = Finder(settings).findFolders()

    # step2: find zip archives in the found folders
    zipsettings = {'regex': r'myarchive.*\.zip', 'caseSensitive': False}
    zips = []
    for folder in folders:
        zipsettings['parent'] = folder
        zipFile = Finder(zipsettings).findFiles()
        if zipFile:
            zips+=zipFile

    # step3: find xml files in zip archives
    xmlsettings = {'regex': r'.*\.xml', 'stopWhenFound':False, 'caseSensitive': False}
    xmls = []
    for zip in zips:
        xmlsettings['parent'] = zip
        xmlFiles = Finder(xmlsettings).findFilesInZip()
        if xmlFiles:
            xmls += xmlFiles

    print(*xmls, sep='\n')
```
                

### Example2
Suppose that you want to let a user search for files, in a ftp repository, based on a regex after prompting for its username and password to connect the ftp server, and for regex to look for specific files. The search should not look into .git folders.  

```python
from pyFileFinder import Finder
import os
from ftplib import FTP, error_perm
from socket import gaierror
import getpass


if __name__ == "__main__":

    settings={'parent':'/', 'avoidFolders':['.git'], 'stopWhenFound': False}

    connection = None
    while not connection:
        user = input(
            'login: ') if not 'user' in settings else settings['user'] if not 'user' in settings else settings['user']
        pwd = getpass.getpass() if not 'pwd' in settings else settings['pwd'] if not 'pwd' in settings else settings['pwd']
        try:
            connection = FTP('type-in-yours.host', user, pwd)
        except error_perm:
            print('wrong login or password')
        except gaierror:
            print('wrong ftp host address')
            input("Press Enter to end...")
            exit()

    settings['ftpConnection'] = connection
    
    settings['regex'] = input(
        'search: ') if not 'regex' in settings else settings['regex']

    files = Finder(settings).findFilesInFtp()

    if not files:
        print('no file found')
    else:
        print(*files, sep='\n')

    input("Press Enter to end...")

```

## Note
Import logging and configure it to display messages in terminal.  
To dot it easily, just add these lines:
```python
from pyBaseApp.configuration import Configuration
import logging
settings = Configuration().default('findFtp')
```

Using pyBaseApp.configuration, it is also possible to define the settings in a yml file named "findFtp.yml"  
(it should be the name given by the argument of default, omitting ".yml")
