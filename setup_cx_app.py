# -*- coding: utf-8 -*-

import os
import importlib.util
import sys
# DO NOT REMOVE setuptools IMPORT: IT PREVENTS AN ERROR SEE https://github.com/anthony-tuininga/cx_Freeze/issues/308
import setuptools
from envswitch.utils import version_file_cx_freeze, get_version
from setuptools_scm import version_from_scm
from cx_Freeze import setup, Executable

# To build
# - the executable distribution, do:  python setup_cx_app.py build   >> result is in build/exe.<target>/
# - the msi installer, do: python setup_cx_app.py bdist_msi          >> result is in dist/envswitch-<ver>-<target>.msi

# First import setup.py so that we can get all description, metadata, etc.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
print('Importing definitions from setup.py...')
spec = importlib.util.spec_from_file_location("setup", os.path.join(THIS_DIR, "setup.py"))
setup_py = importlib.util.module_from_spec(spec)
tmp = sys.argv  # temporarily store the sys.argv to replace them during this call
sys.argv = [tmp[0].replace('setup_cx_app.py', 'setup.py'), '--quiet', '--dry-run', 'clean']  # performs nothing, simply loads the variables defined in the script
spec.loader.exec_module(setup_py)
print('DONE, now executing setup_cx_app.py...')
sys.argv = tmp

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"
# other platforms seem ok

# *** find the folder containing the qt platform plugins ****
# -- Create a dummy app in order to load the appropriate qt configuration for the system.
# app = QApplication(sys.argv)
# plugins_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
# qt_platforms_folder = os.path.join(plugins_path, 'platforms')
# unfortunately for some reason the dll files from while the one from Anaconda/Library/plugins/platforms work,
# so we included the latter in the sources just in case..
qt_platforms_folder = os.path.join(THIS_DIR, 'qt_resources', 'platforms')

# # you should pip install -e . before running this
# import pkg_resources  # part of setuptools
# _app_version = pkg_resources.require("envswitch")[0].version
# we have to manually create a version number compliant with cx_Freeze (no letters, just numbers)
my_version = version_from_scm(THIS_DIR)
if my_version is not None:
    THIS_TAG_OR_NEXT_TAG_VERSION = my_version.format_with("{tag}")
    with open('./' + version_file_cx_freeze, 'wt') as f:
        f.write(THIS_TAG_OR_NEXT_TAG_VERSION)
else:
    print('WARNING: the version will not be retrieved from git but from the previously created '
          + version_file_cx_freeze + ' file. This is ok if you ran python setup_cx_app.py build beforehand')
    THIS_TAG_OR_NEXT_TAG_VERSION = get_version()

# Dependencies are automatically detected, but it might need fine tuning.
# unpackEgg('setuptools', 'eggs_tmp')  # setuptools contains 'pkg_resources'
options = {
    # see http://cx-freeze.readthedocs.io/en/latest/distutils.html#build-exe
    'build_exe': {
        'includes': [],
        'packages': ['os'],  #, 'pkg_resources'],
        'excludes': ['*'],
        "include_files": [# (os.path.join(THIS_DIR, 'qt_resources', 'qt.conf'), 'qt.conf'),  not needed, default is ok
                          (qt_platforms_folder, 'platforms'),  # in order to override the one gathered by cx_Freeze
                          'LICENSE',
                          version_file_cx_freeze,
                          'README.md'],  # relative paths only
        # "include_msvcr"=True
        # 'path': sys.path + ['eggs_tmp']
    }
}

executables = [
    # see http://cx-freeze.readthedocs.io/en/latest/distutils.html#cx-freeze-executable
    Executable(script='envswitch/gui.py',
               # initScript= (executed before script)
               targetName='envswitch.exe',
               base=base,
               # icon=
               )
]


setup(name=setup_py.DISTNAME,
      description=setup_py.DESCRIPTION,
      long_description=setup_py.LONG_DESCRIPTION,

      # Versions should comply with PEP440.  For a discussion on single-sourcing
      # the version across setup_py.py and the project code, see
      # https://packaging.python.org/en/latest/single_source_version.html
      # version=setup_py.THIS_TAG_OR_NEXT_TAG_VERSION, NOW HANDLED BY GIT

      maintainer=setup_py.MAINTAINER,
      maintainer_email=setup_py.MAINTAINER_EMAIL,

      license=setup_py.LICENSE,
      url=setup_py.URL,
      download_url=setup_py.DOWNLOAD_URL,

      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 4 - Beta',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Desktop Environment',
          # 'Topic :: Software Development :: Libraries :: Python Modules',

          # Pick your license as you wish (should match "license" above)
          setup_py.LICENSE_LONG,

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          # 'Programming Language :: Python :: 2',
          # 'Programming Language :: Python :: 2.6',
          # 'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3',
          # 'Programming Language :: Python :: 3.3',
          # 'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],

      # What does your project relate to?
      keywords=setup_py.KEYWORDS,

      # setuptools_scm to detect git version. Unfortunately this does not work with cx_Freeze (unsupported dev)
      # use_scm_version=True,
      version=THIS_TAG_OR_NEXT_TAG_VERSION,

      # cx_Freeze specific
      options=options,
      executables=executables,
      )
