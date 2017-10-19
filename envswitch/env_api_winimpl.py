import sys
from typing import Dict, Any
from warnings import warn
from winreg import *

import subprocess

try:
    import win32gui, win32con
except Exception as e:
    print('This requires to install pywin32 (conda) / pypiwin32 (pip)')
    raise e


def get_env_with_cmd_win(var_name, whole_machine: bool = False):
    """
    Similar to os.environ[var_name] but reads the environment variable as defined at the os USER (default) or MACHINE
    level (if whole_machine = True), not the value of the environment variable in the current process context

    :param var_name:
    :param whole_machine: if True the env variable will be looked up in the MACHINE env variables. If False it will be
    done at USER level
    :return:
    """
    # --Works but the subprocess inherits from the parent environment so it is NOT a truly independent observation
    # proc = subprocess.Popen('cmd /c set ' + var_name, stdout=subprocess.PIPE)
    # resbytestr = proc.stdout.read()
    # resstr = resbytestr.decode(encoding=sys.stdout.encoding)
    # if resstr.startswith(var_name + '='):
    #     return resstr[len(var_name + '='):].replace('\r','').replace('\n','')
    # else:
    #     # undefined
    #     return None

    try:
        # Maybe one day instead first try at user environment variables then try at system environment variables
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE if whole_machine else HKEY_CURRENT_USER)
        path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment' if whole_machine else r'Environment'
        key = _open_key(reg, path, whole_machine)
        return query_value_win(path, key, var_name, whole_machine)
    finally:
        # Always try to close everything in reverse order, silently
        try:
            CloseKey(key)
        except:
            pass
        try:
            CloseKey(reg)
        except:
            pass


def set_env_variables_permanently_win(key_value_pairs: Dict[str, Any], whole_machine: bool = False):
    """
    Similar to os.environ[var_name] = var_value for all pairs provided, but instead of setting the variables in the
    current process, sets the environment variables permanently at the os MACHINE level.

    Recipe from http://code.activestate.com/recipes/416087/
    :param key_value_pairs: a dictionary of variable name+value to set
    :param whole_machine: if True the env variables will be set at the MACHINE (HKLM) level. If False it will be
    done at USER level (HKCU)
    :return:
    """

    try:
        path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment' if whole_machine else r'Environment'
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE if whole_machine else HKEY_CURRENT_USER)
        key = _open_key(reg, path, whole_machine)

        if key_value_pairs is None:
            # print all values..
            show_win(key)
        else:
            for name, value in key_value_pairs.items():
                if name.upper() == 'PATH':
                    # TODO maybe remove this security ?
                    warn('PATH can not be entirely changed. The value will be simply appended at the end.')
                    value = query_value_win(path, key, name, whole_machine) + ';' + value
                if value:
                    print("Setting ENV VARIABLE '" + name + "' to '" + value + "'")
                    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
                else:
                    print("Deleting ENV VARIABLE '" + name + "'")
                    try:
                        DeleteValue(key, name)
                    except FileNotFoundError:
                        # ignore if already deleted
                        pass

            # this hangs forever, see https://stackoverflow.com/questions/1951658/sendmessagehwnd-broadcast-hangs
            # win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
            print("Broadcasting change to other windows")
            win32gui.SendMessageTimeout(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment',
                                        win32con.SMTO_ABORTIFHUNG, 1000)

    finally:
        # Always try to close everything in reverse order, silently
        try:
            CloseKey(key)
        except:
            pass
        try:
            CloseKey(reg)
        except:
            pass


def _open_key(reg, path, whole_machine: bool):
    """
    Opens registry key at `path` on already connected registry `reg`. whole_machine is there for error messages, to

    :param reg:
    :param path:
    :param whole_machine:
    :return:
    """
    try:
        return OpenKey(reg, path, 0, KEY_SET_VALUE | KEY_QUERY_VALUE)  # KEY_ALL_ACCESS
    except PermissionError as e:
        keystr = ('HKEY_LOCAL_MACHINE' if whole_machine else 'HKEY_CURRENT_USER') + ':' + path
        raise Exception("Encountered a PermissionError while opening WINDOWS registry key '" + keystr + "'. You may "
                        "need to run this program as an Administrator").with_traceback(e.__traceback__)


def query_value_win(path: str, key, var_name: str, whole_machine: bool):
    """
    Reads a registry key. Throws a FileNotFoundError if it does not exist

    :param path: for the warning message.
    :param key: an already opened registry key
    :param var_name:
    :param whole_machine: for the warning message.
    :return:
    """
    try:
        value, type_id = QueryValueEx(key, var_name)
        return value
    except FileNotFoundError:
        keystr = ('HKEY_LOCAL_MACHINE' if whole_machine else 'HKEY_CURRENT_USER') + ':' + path
        warn("Environment variable '" + var_name + "'not found under WINDOWS registry key '" + keystr + "'")
        return ''


def show_win(key):
    """
    Print all registry values registered under key

    :param key:
    :return:
    """
    for i in range(1024):
        try:
            n,v,t = EnumValue(key, i)
            print('%s=%s' % (n, v))
        except EnvironmentError:
            break
