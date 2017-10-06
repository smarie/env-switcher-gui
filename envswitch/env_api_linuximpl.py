from typing import Dict, Any


def get_env_with_cmd_linux(var_name):
    """
    TODO: Similar to os.environ[var_name] but reads the environment variable as defined at the os MACHINE/SYSTEM level,
    not the value of the environment variable in the current process context

    :param var_name:
    :return:
    """
    raise NotImplementedError()


def set_env_variables_permanently_linux(key_value_pairs: Dict[str, Any]):
    """
    TODO: Similar to os.environ[var_name] = var_value for all pairs provided, but instead of setting the variables in
    the current process, sets the environment variables permanently at the os MACHINE/SYSTEM level.

    :return:
    """
    raise NotImplementedError()
