#!/usr/bin/env python3

import json
import os
import sys
import shutil
import fnmatch
import functools
import itertools

# define additional patterns for files here that are not in the .gitignore file and should be omitted from the zipped mod
additionalIgnorePatterns = ['*.py', '.git', '.gitignore']

# reads non-commented ignore patterns from the .gitignore file
def readGitIgnorePatterns():
  patterns = set()

  if os.path.isfile('.gitignore'):
    with open('.gitignore') as gitIgnoreFile:
      for line in gitIgnoreFile:
        if not line.startswith('#'):
          if line.endswith('\n'):
            patterns.add(line[:-1])
          else:
            patterns.add(line)

  return patterns

# taken from http://stackoverflow.com/questions/5351766/use-fnmatch-filter-to-filter-files-by-more-than-one-possible-file-extension/25413436#25413436
# modified for ignoreFunction use
def find_files(dir_path: str=None, patterns: [str]=None) -> [str]:
    path = dir_path or "."
    path_patterns = patterns or []

    file_names = os.listdir(path)
    filter_partial = functools.partial(fnmatch.filter, file_names)

    for file_name in itertools.chain(*map(filter_partial, path_patterns)):
        yield file_name

# function to be passed to copytree, see https://docs.python.org/2/library/shutil.html#shutil.copytree
def ignoreFunction(directory, files):
  ignorePatterns = readGitIgnorePatterns()
  ignorePatterns = list(ignorePatterns)

  for additionalPattern in additionalIgnorePatterns:
    ignorePatterns.append(additionalPattern)

  ignoredFiles = [file for file in find_files(directory, ignorePatterns)]

  return ignoredFiles

## script start
if len(sys.argv) == 2:
  dir = sys.argv[1]
else:
  dir = '.'

with open(os.path.join(dir, 'info.json')) as infoFile:
  modInfo = json.load(infoFile)

if modInfo is not None:
  modName = modInfo['name']
  modVersion = modInfo['version']

  modFileName = modName + '_' + modVersion
  tempDir = os.path.join ('.', 'tmp')
  modDir = os.path.join(tempDir, modFileName)

  shutil.copytree(dir, modDir, ignore=ignoreFunction)

  if os.path.isfile(modFileName + '.zip'):
    os.remove(modFileName + '.zip')

  shutil.make_archive(modFileName, 'zip', tempDir)
  shutil.rmtree(tempDir)