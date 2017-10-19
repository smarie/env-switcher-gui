import os
from os import getenv

import sys
from warnings import warn

import envswitch as es


def test_env_switch():
    """
    reads the value for the http_proxy environment variable, replaces it with 'blah', checks that it has been set
    correctly, and sets it back to initial value.
    :return:
    """

    # this environment variable needs to exist outside of the current terminal
    if sys.platform == "win32":
        env_var = 'OS'  # it needs to ba a system/machine variable, not a user-scoped one
    else:
        env_var = 'HOME'

    # (1) get and save initial value
    init_val = getenv(env_var)

    # print the initial value
    print(env_var + '=' + init_val)
    es.print_external_env_var(env_var, whole_machine=True)

    # assert getting from external provides the same value
    assert es.get_external_env_var(env_var, whole_machine=True) == init_val

    try:
        # (2) set a new value permanently
        es.set_env_permanently(env_var, 'blah >', whole_machine=True)

        # print the changed value and assert
        es.print_external_env_var(env_var, whole_machine=True)
        assert es.get_external_env_var(env_var, whole_machine=True) == 'blah >'
        # TODO later version
        # assert os.getenv(env_http_proxy) == 'blah >'

        # (3) set to initial value permanently
        es.set_env_permanently(env_var, init_val, whole_machine=True)

        # get and assert
        es.print_external_env_var(env_var, whole_machine=True)
        assert es.get_external_env_var(env_var, whole_machine=True) == init_val

    except Exception as e:
        # safety
        if es.get_external_env_var(env_var, whole_machine=True) != init_val:
            raise Exception('WARNING: the test execution failed and your environment is left in a BAD state. Please set'
                            ' back the following environment variable : ' + env_var + '=' + init_val + '. Initial error'
                            ' is ' + str(e)).with_traceback(e.__traceback__)
