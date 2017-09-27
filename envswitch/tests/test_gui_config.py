import os
import tempfile

import pytest

from envswitch.env_config import GlobalEnvsConfig

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("config_file_name", os.listdir(os.path.join(THIS_DIR, 'data')))
def test_load_gui_config(config_file_name: str):
    conf_file_path = os.path.join(THIS_DIR, 'data', config_file_name)

    # first load the configuration
    with open(conf_file_path, 'r') as f:
        conf = GlobalEnvsConfig.from_yaml(f)
        assert type(conf) == GlobalEnvsConfig

    # then create a temp file, dump it here and read it again
    fd, fpath = tempfile.mkstemp(text=True)
    try:
        # dump to file
        with open(fpath, mode='w') as f:
            conf.to_yaml(f)

        # read from file
        with open(fpath, mode='r') as f:
            conf2 = GlobalEnvsConfig.from_yaml(f)

        # compare the two
        assert conf.to_yaml() == conf2.to_yaml()
        assert conf == conf2

    finally:
        # remove the temporary file
        os.close(fd)
        os.remove(fpath)

