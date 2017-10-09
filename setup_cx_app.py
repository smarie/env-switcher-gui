# -*- coding: utf-8 -*-
import os
import importlib.util
import shutil
import sys
# DO NOT REMOVE setuptools IMPORT: IT PREVENTS AN ERROR SEE https://github.com/anthony-tuininga/cx_Freeze/issues/308
import setuptools
from envswitch.utils import version_file_cx_freeze, get_version
from setuptools_scm import version_from_scm
from cx_Freeze import setup, Executable, build_exe

# To build
# - the executable distribution, do:  python setup_cx_app.py build   >> result is in build/exe.<target>/
# - the msi installer, do: python setup_cx_app.py bdist_msi          >> result is in dist/envswitch-<ver>-<target>.msi

# First import setup.py so that we can get all description, metadata, etc.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
print('Importing definitions from setup.py...')
spec = importlib.util.spec_from_file_location("setup", os.path.join(THIS_DIR, "setup.py"))
setup_py = importlib.util.module_from_spec(spec)
tmp = sys.argv  # temporarily store the sys.argv to replace them during this call
sys.argv = [tmp[0].replace('setup_cx_app.py', 'setup.py'), '--quiet', '--dry-run',
            'clean']  # performs nothing, simply loads the variables defined in the script
spec.loader.exec_module(setup_py)
print('DONE, now executing setup_cx_app.py...')
sys.argv = tmp


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

# turn this on to enable debug messages if you dont understand why such module is not imported
# import logging
# logging.getLogger().setLevel(logging.DEBUG)

# ******** define what to include in the frozen version *********
files_to_include = ['LICENSE', 'LICENSE-PyQt', 'LICENSE-Qt', version_file_cx_freeze, 'README.md']
# unfortunately for some reason the dll files from the current anaconda env do not work,
# while the one from root (Anaconda/Library/plugins/platforms) works, so we include the latter in the sources
qt_platforms_folder = os.path.join(THIS_DIR, 'qt_resources', 'platforms')
if sys.platform == "win32":
    files_to_include.append((qt_platforms_folder, 'platforms')),  # in order to override the one gathered by cx_Freeze

options = {
    # see http://cx-freeze.readthedocs.io/en/latest/distutils.html#build-exe
    'build_exe': {
        # ---- Dependencies are automatically detected, but too much is included. Fine-tune ----
        # Unfortunately as os cx_Freeze 5.0.2 there is absolutely NO way to include PyQt5.Qt, QtCore, QtGui, QtWidgets
        # without including the parent package PyQt5 entirely :( so we have to remove it later in a hack, see line 81
        'includes': [],
        'packages': ['os'],
        # 'excludes': [],
        'excludes': ['numpy', 'pydoc', 'pydoc_data', 'email', 'multiprocessing', 'contracts', 'unittest', 'urllib',
                     'xml', 'xmlrpc', 'bz2', 'ssl', 'hashlib', 'socket', 'lzma', 'unicodedata', 'html', 'http',
                     'distutils'],
        # 'bin_excludes': [],
        'bin_excludes': ['pywintypes35.dll', 'zlib.dll', 'libpng16.dll', 'mkl_intel_thread.dll',
                         'icudt58.dll', 'icuin58.dll', 'icuuc58.dll',
                         'icudt57.dll', 'icuin57.dll', 'icuuc57.dll',
                         'platforms/libqminimal.so', 'platforms/libqoffscreen.so', 'libQt5DBus.so.5', 'libQt5Svg.so.5',
                         'libQt5XcbQpa.so.5', 'libxml2.so.2', 'libjpeg.so.9', 'liblzma.so.5', 'libfreetype.so.6',
                         'libdbus-1.so.3', 'libfontconfig.so.1', 'libreadline.so.7', 'libtinfow.so.6', 'libxcb.so.1',
                         ],
        # ---- other files to include ------
        "include_files": files_to_include,
        # "include_msvcr"=False
        'optimize': 2
    }
}


# ********* Hack to remove qt files after build ****************
super_run = build_exe.run
def run(self):
    super_run(self)
    print('HACK: removing part of the PyQt5 module to reduce the final size')
    # first find the folder
    import glob
    all = [folder for folder in glob.glob(self.build_exe + '/**/PyQt5', recursive=True)]
    if len(all) > 1:
        raise Exception('Found several PyQt5 folders... ' + str(all))
    if len(all) == 1:
        # then remove all unused files
        pyqt_dir = all[0]
        for f in os.listdir(pyqt_dir):
            if f.startswith('QtCore') or f.startswith('QtGui') or f.startswith('QtWidget') or f.startswith('__'):
                # keep it
                pass
            else:

                path = os.path.join(pyqt_dir, f)
                if os.path.isfile(path):
                    print('Removing file: ' + path)
                    os.remove(path)
                else:
                    print('Removing folder: ' + path)
                    shutil.rmtree(path)
    print('DONE')
build_exe.run = run  # this is where we replace the methods with our hack
# *************************


# ********* define executables to create ****************
executables = []
if sys.platform == "win32":
    # on Windows, create base=None for a console application (debug mode)
    executables.append(
        Executable(script='envswitch/gui.py',
                   # initScript= (executed before script)
                   targetName='envswitch_debug.exe',
                   base=None,
                   # icon=
                   )
    )
    # AND create a GUI also
    base = "Win32GUI"
else:
    # other platforms seem ok
    base = None

executables.append(
    # see http://cx-freeze.readthedocs.io/en/latest/distutils.html#cx-freeze-executable
    Executable(script='envswitch/gui.py',
               # initScript= (executed before script)
               targetName='envswitch.exe',
               base=base,
               # icon=
               )
)
# *************************


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
