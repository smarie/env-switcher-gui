import sys

import os

version_file_cx_freeze = 'VERSION__'


def get_version():
    """
    Utility to find the version of this application whatever the execution mode (cx_Freeze or normal)
    :return:
    """
    if getattr(sys, "frozen", False):
        # this is cx_Freeze execution mode >> access our generated file
        datadir = os.path.dirname(sys.executable)
        path = os.path.join(datadir, version_file_cx_freeze)
        with open(path, 'rt') as f:
            return f.read()
    else:
        import pkg_resources  # part of setuptools
        from pkg_resources import DistributionNotFound
        try:
            return pkg_resources.require("envswitch")[0].version
        except DistributionNotFound as e:
            # this may happen if the module has not been even locally installed with "pip install ."
            from setuptools_scm import get_version
            return get_version()


def get_resource_path(relative_path):
    """
    Utility to find resource files whatever the running mode
    :param relative_path:
    :return:
    """
    if getattr(sys, "frozen", False):
        # The application is frozen using cx_Freeze.
        datadir = os.path.dirname(sys.executable)
        return os.path.join(datadir, relative_path)
    else:
        # The application is not frozen.
        import pkg_resources
        return pkg_resources.resource_filename('envswitch', relative_path)
