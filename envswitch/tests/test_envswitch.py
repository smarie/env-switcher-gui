import os
from os import getenv

import envswitch as es


def test_env_switch():
    """
    reads the value for the http_proxy environment variable, replaces it with 'blah', checks that it has been set
    correctly, and sets it back to initial value.
    :return:
    """

    # (1) get and save initial value
    env_var = 'path'
    init_val = getenv(env_var)

    # print the initial value
    print(env_var + '=' + init_val)
    es.print_external_env_var(env_var)

    # assert getting from external provides the same value
    assert es.get_external_env_var(env_var) == init_val

    # (2) set a new value permanently
    es.set_env_permanently(env_var, 'blah')

    # print the changed value and assert
    es.print_external_env_var(env_var)
    assert es.get_external_env_var(env_var) == 'blah'
    # TODO later version
    # assert os.getenv(env_http_proxy) == 'blah'

    # (3) set to initial value permanently
    es.set_env_permanently(env_var, init_val)

    # get and assert
    es.print_external_env_var(env_var)
    assert es.get_external_env_var(env_var) == init_val
