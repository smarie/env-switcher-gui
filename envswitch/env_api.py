import os
import platform
from multiprocessing import Queue


# --not needed anymore
# import multiprocessing as mp
# try:
#     mp.set_start_method('spawn')
# except RuntimeError:
#     # normal the second time this is called (or in the spawned processes)
#     pass
from typing import Dict, Any


def print_external_env_var(var_name):
    print('Value for ' + var_name + ' is : ' + get_external_env_var(var_name))


def getenv(var_name, q: Queue):
    """
    A method to be spawned in a separate process to get an environment variable's value.
    :param var_name:
    :param q:
    :return:
    """
    q.put(os.getenv(var_name))


def get_external_env_var(var_name):
    """
    Similar to  os.getenv(var_name) but uses a command process to check the variable value out of this process

    :param var_name:
    :return:
    """
    case = check_platform_and_get_case()
    if case is WINDOWS:
        from envswitch.env_api_winimpl import get_env_with_cmd_win
        return get_env_with_cmd_win(var_name)

    # #spawn an independnt process that will start from fresh environment variables context ?
    # > spawning works but it still gets the parent environment :(
    # q = mp.Queue()
    # p = mp.Process(target=getenv, args=(var_name,q))
    #
    # # start the process
    # p.start()
    #
    # # get the results of the python method called
    # res = q.get()
    #
    # # wait for termination of the spawned process
    # p.join()
    #
    # return res


WINDOWS = 1


def set_env_permanently(env_varname, env_value):
    """
    Similar to os.setenv(var_name, value) but performs a permanent change, not just for the current process.

    :param env_varname:
    :param env_value:
    :return:
    """
    set_env_variables_permanently({env_varname: env_value})


def set_env_variables_permanently(key_value_pairs: Dict[str, Any]):
    """
    Similar to set_env_permanently but for a dictionary of environment variable names/value
    :param key_value_pairs:
    :return:
    """
    case = check_platform_and_get_case()
    if case is WINDOWS:
        from envswitch.env_api_winimpl import set_env_variables_permanently_win
        set_env_variables_permanently_win(key_value_pairs)
    else:
        raise NotImplementedError('Code for this platform is missing in envswitch, please create an issue '
                                  'on the github project page and optionally propose a pull request')


def check_platform_and_get_case() -> int:
    """
    Checks that the OS and version is supported
    :return:
    """
    system = platform.system()
    release = platform.release()
    version = platform.version()
    if system == 'Windows':
        return WINDOWS
    else:
        raise ValueError('This operating system/version is currently unsupported: ' + platform.platform())





