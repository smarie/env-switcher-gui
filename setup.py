"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import platform
import sys
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# *************** Dependencies *********
try:
    from PyQt5 import QtCore
except ImportError as e:
    print('This package requires PyQt with version 5.6 (later versions generate distribution issues).')
    raise e

INSTALL_REQUIRES = ['pyyaml', 'click', 'autoclass']  # we cannot include 'PyQt>=5.6' here for conda compatibility reasons, see doc/index.md
DEPENDENCY_LINKS = []
SETUP_REQUIRES = ['pytest-runner', 'setuptools_scm', 'pypandoc', 'pandoc']
TESTS_REQUIRE = ['pytest', 'pytest-logging', 'pytest-cov']

# Unfortunately this does not enforce the installation with pip. And the package does not have the same name on conda!
# EXTRAS_REQUIRE = {':sys_platform == "win32"': ['pypiwin32'],  #    'platform_system=="Windows"'
#                   #':"linux" in sys_platform': ['pyxdg']    # 'platform_system=="Linux"'
#                  }
print('Checking platform. If Windows, enforcing pywin32/pypiwin32')
system = platform.system()
if system == 'Windows':
    try:
        import win32gui, win32con
    except ImportError as e:
        print('This requires to install pywin32 (conda) / pypiwin32 (pip)')
        raise e
EXTRAS_REQUIRE = {}

# simple check
try:
    from setuptools_scm import get_version
except Exception as e:
    raise Exception('Required packages for setup not found. You may wish you execute '
                    '"pip install -r ci_tools/requirements-setup.txt" to install them or alternatively install them '
                    'manually using conda or other system. The list is : ' + str(SETUP_REQUIRES)) from e

# ************** ID card *****************
DISTNAME = 'envswitch'
DESCRIPTION = 'A very simple GUI and CLI to manage environment variables.'
MAINTAINER = 'Sylvain Marié'
MAINTAINER_EMAIL = 'sylvain.marie@schneider-electric.com'
URL = 'https://github.com/smarie/env-switcher-gui'
LICENSE = 'BSD 3-Clause'
LICENSE_LONG = 'License :: OSI Approved :: BSD License'

version_for_download_url = get_version()
DOWNLOAD_URL = URL + '/tarball/' + version_for_download_url

KEYWORDS = 'env-variable environment variable http proxy switch gui cli desktop application'

# --Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#    LONG_DESCRIPTION = f.read()
try:
    import pypandoc
    print('converting readme to RST')
    LONG_DESCRIPTION = pypandoc.convert(path.join(here, 'README.md'), 'rst').replace('\r', '')

    # Validate that the generated doc is correct
    print('validating generated rst readme')
    from docutils.parsers.rst import Parser
    from docutils.utils import new_document
    from docutils.frontend import OptionParser
    # import pygments
    settings = OptionParser(components=(Parser,)).get_default_values()
    document = new_document('(generated) DESCRIPTION.rst', settings=settings)

    from distutils.command.check import SilentReporter
    reporter = SilentReporter('(generated) DESCRIPTION.rst',
                              settings.report_level,
                              settings.halt_level,
                              stream=settings.warning_stream,
                              debug=settings.debug,
                              encoding=settings.error_encoding,
                              error_handler=settings.error_encoding_error_handler)
    document.reporter = reporter
    parser = Parser()
    parser.parse(LONG_DESCRIPTION, document)
    from warnings import warn
    if len(reporter.messages) > 0:
        # display all errors
        for warning in reporter.messages:
            line = warning[-1].get('line')
            if line is None:
                warning = warning[1]
            else:
                warning = '%s (line %s)' % (warning[1], line)
            warn(warning)
        # dump the created file so that one can have a look
        with open('GENERATED_DESCRIPTION_TO_DELETE.rst', 'wb') as f:
            f.write(LONG_DESCRIPTION.encode('utf-8'))
        print('There are warnings in the generated DESCRIPTION.rst. The created description file has been dumped to '
              'GENERATED_DESCRIPTION_TO_DELETE.rst temporary file for review')
        sys.exit(1)

except(ImportError):
    from warnings import warn
    warn('WARNING pypandoc and/or docutils could not be imported - we recommend that you install them in order to '
         'package the documentation correctly')
    LONG_DESCRIPTION = open('README.md').read()

# ************* THIS_TAG_OR_NEXT_TAG_VERSION A **************
# --Get the Version number from THIS_TAG_OR_NEXT_TAG_VERSION file, see https://packaging.python.org/single_source_version/ option 4.
# THIS IS DEPRECATED AS WE NOW USE GIT TO MANAGE THIS_TAG_OR_NEXT_TAG_VERSION
# with open(path.join(here, 'THIS_TAG_OR_NEXT_TAG_VERSION')) as version_file:
#    THIS_TAG_OR_NEXT_TAG_VERSION = version_file.read().strip()


# ************* EMBEDDED RESOURCES **************
# PACKAGE_DATA = {'tsregcore': ['demo/*'],}

# ************* ENTRY POINTS = COMMANDS THAT WILL BECOME AVAIBLE
ENTRY_POINTS={'console_scripts': ['envswitch = envswitch.cli:cli',
                                  'envswitch_gui_debug = envswitch.gui:main'],  # this will print in the console
              'gui_scripts':     ['envswitch_gui = envswitch.gui:main']}        # this wont

setup(
    name=DISTNAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    # version=THIS_TAG_OR_NEXT_TAG_VERSION, NOW HANDLED BY GIT

    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,

    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,

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
        LICENSE_LONG,

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
    keywords=KEYWORDS,

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,

    # we're using git
    use_scm_version=True,  # this provides the version + adds the date if local non-commited changes.
    # use_scm_version={'local_scheme':'dirty-tag'}, # this provides the version + adds '+dirty' if local non-commited changes.
    setup_requires=SETUP_REQUIRES,

    # test
    # test_suite='nose.collector',
    tests_require=TESTS_REQUIRE,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require=EXTRAS_REQUIRE,

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        # the key should be the package name !
        'envswitch': ['resources/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],
    # data_files=[('docs', ['docs/DesignOverview.png'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points=ENTRY_POINTS,
)
