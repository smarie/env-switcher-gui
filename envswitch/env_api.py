import os
import platform


# --not needed anymore
# import multiprocessing as mp
# try:
#     mp.set_start_method('spawn')
# except RuntimeError:
#     # normal the second time this is called (or in the spawned processes)
#     pass
from typing import Dict, Any


def print_external_env_var(var_name, whole_machine: bool=False):
    """

    :param var_name:
    :param whole_machine: if True the env variables will be read from the MACHINE level. If False it will be read from
    USER level
    :return:
    """
    print('Value for ' + var_name + ' is : ' + get_external_env_var(var_name, whole_machine=whole_machine))


# def getenv(var_name, q: mp.Queue):
#     """
#     A method to be spawned in a separate process to get an environment variable's value.
#     :param var_name:
#     :param q:
#     :return:
#     """
#     q.put(os.getenv(var_name))


def get_external_env_var(var_name, whole_machine: bool=False):
    """
    Similar to  os.getenv(var_name) but uses a command process to check the variable value out of this process

    :param var_name:
    :param whole_machine: if True the env variables will be read from the MACHINE level. If False it will be read from
    USER level
    :return:
    """
    case = check_platform_and_get_case()
    if case is WINDOWS:
        from envswitch.env_api_winimpl import get_env_with_cmd_win
        return get_env_with_cmd_win(var_name, whole_machine=whole_machine)

    elif case is LINUX:
        from envswitch.env_api_linuximpl import get_env_with_cmd_linux
        return get_env_with_cmd_linux(var_name, whole_machine=whole_machine)

    else:
        raise NotImplementedError('Code for this platform is missing in envswitch, please create an issue '
                                  'on the github project page and optionally propose a pull request')
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
LINUX = 2


def set_env_permanently(env_varname, env_value, also_apply_on_this_process: bool=True, whole_machine: bool = False):
    """
    Similar to os.setenv(var_name, value) but performs a permanent change, not just for the current process.

    :param env_varname:
    :param env_value:
    :param also_apply_on_this_process:
    :param whole_machine: if True the env variables will be set at the MACHINE level. If False it will be done at
    USER level
    :return:
    """
    set_env_variables_permanently({env_varname: env_value},also_apply_on_this_process=also_apply_on_this_process,
                                  whole_machine=whole_machine)


def set_env_variables_permanently(key_value_pairs: Dict[str, Any], also_apply_on_this_process: bool=True,
                                  whole_machine: bool = False):
    """
    Similar to set_env_permanently but for a dictionary of environment variable names/value

    :param key_value_pairs:
    :param also_apply_on_this_process:
    :param whole_machine: if True the env variables will be set at the MACHINE level. If False it will be done at
    USER level
    :return:
    """
    # -- permanent (all new processes) application
    case = check_platform_and_get_case()
    if case is WINDOWS:
        from envswitch.env_api_winimpl import set_env_variables_permanently_win
        set_env_variables_permanently_win(key_value_pairs, whole_machine)

    elif case is LINUX:
        from envswitch.env_api_linuximpl import set_env_variables_permanently_linux
        set_env_variables_permanently_linux(key_value_pairs, whole_machine)

    else:
        raise NotImplementedError('Code for this platform is missing in envswitch, please create an issue '
                                  'on the github project page and optionally propose a pull request')

    # -- local (this commandline if any)
    # TODO next version
    # refresher_cmd = get_resource_path('./resources/win/RefreshEnv.cmd')
    # call([refresher_cmd])
    # Popen([refresher_cmd])

    # -- local (this running process) application. Only useful for usage within a python script
    if also_apply_on_this_process:
        for var_name, value in key_value_pairs.items():
            if value:
                os.environ[var_name] = value
            else:
                try:
                    del os.environ[var_name]
                except KeyError:
                    # ignore if already deleted
                    pass


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
    elif system == 'Linux':
        return LINUX
    else:
        raise ValueError('This operating system/version is currently unsupported: ' + platform.platform())
