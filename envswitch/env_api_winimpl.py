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


def get_env_with_cmd_win(var_name):
    """
    Similar to os.environ[var_name] but reads the environment variable as defined at the os MACHINE level, not the
    value of the environment variable in the current process context

    :param var_name:
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
        # try:
        #     # first try at user environment variables
        #     reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        #     path = r'Environment'
        #     key = OpenKey(reg, path, 0, KEY_ALL_ACCESS)
        #     value = query_value_win(key, var_name)
        # except FileNotFoundError:
        #     # close the first one
        #     CloseKey(key)
        #     CloseKey(reg)
        # then try at system environment variables
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        key = OpenKey(reg, path, 0, KEY_ALL_ACCESS)
        try:
            value = query_value_win(key, var_name)
            return value
        except FileNotFoundError:
            warn('Environment variable not found in WINDOWS HKEY_LOCAL_MACHINE. Note that this program does not '
                 'interact with user-scope environment variables')
            return ''
    finally:
        CloseKey(key)
        CloseKey(reg)


def set_env_variables_permanently_win(key_value_pairs: Dict[str, Any]):
    """
    Similar to os.environ[var_name] = var_value for all pairs provided, but instead of setting the variables in the
    current process, sets the environment variables permanently at the os MACHINE level.

    Recipe from http://code.activestate.com/recipes/416087/
    :return:
    """

    try:
        path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        key = OpenKey(reg, path, 0, KEY_ALL_ACCESS)

        if key_value_pairs is None:
            # print all values..
            show_win(key)
        else:
            for name, value in key_value_pairs.items():
                if name.upper() == 'PATH':
                    # TODO maybe remove this security ?
                    warn('PATH can not be entirely changed. The value will be simply appended at the end.')
                    value = query_value_win(key, name) + ';' + value
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
        CloseKey(key)
        CloseKey(reg)


def query_value_win(key, name):
    """
    Reads a registry key. Throws a FileNotFoundError if it does not exist

    :param key:
    :param name:
    :return:
    """
    value, type_id = QueryValueEx(key, name)
    return value


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
