import os
from os import getenv

import envswitch as es


def test_env_switch():
    """
    reads the value for the http_proxy environment variable, replaces it with 'blah', checks that it has been set
    correctly, and sets it back to initial value.
    :return:
    """

    # child_env = os.environ.copy()

    # just for tests
    env_http_proxy = 'http_proxy'

    # save the initial value
    init_val = getenv(env_http_proxy)
    # print the initial value
    es.print_external_env_var(env_http_proxy)
    assert es.get_external_env_var(env_http_proxy) == init_val

    # input("Press Enter to continue and change the HTTP_PROXY...")

    # set a new value permanently
    es.set_env_permanently(env_http_proxy, 'blah')
    es.print_external_env_var(env_http_proxy)
    assert es.get_external_env_var(env_http_proxy) == 'blah'

    # input("Press Enter to continue and change back the HTTP_PROXY...")

    # set a new value permanently
    es.set_env_permanently(env_http_proxy, init_val)
    es.print_external_env_var(env_http_proxy)
    assert es.get_external_env_var(env_http_proxy) == init_val
