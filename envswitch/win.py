import sys
from typing import Dict, Any
from warnings import warn
from winreg import *

import subprocess

try:
    import win32gui, win32con
except ImportError as e:
    print('This requires to install pywin32')
    raise e

def get_env_with_cmd_win(var_name):
    """
    Similar to os.getenv actually
    :param var_name:
    :return:
    """
    # --Works but the subprocess inherits from the parent environment...
    # proc = subprocess.Popen('cmd /c set ' + var_name, stdout=subprocess.PIPE)
    # resbytestr = proc.stdout.read()
    # resstr = resbytestr.decode(encoding=sys.stdout.encoding)
    # if resstr.startswith(var_name + '='):
    #     return resstr[len(var_name + '='):].replace('\r','').replace('\n','')
    # else:
    #     # undefined
    #     return None

    try:
        path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        key = OpenKey(reg, path, 0, KEY_ALL_ACCESS)
        return query_value_win(key, var_name)
    finally:
        CloseKey(key)
        CloseKey(reg)


def set_env_variables_permanently_win(key_value_pairs: Dict[str, Any]):
    """
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
                    warn('PATH can not be entirely changed. The value will be simply appended at the end.')
                    value = query_value_win(key, name) + ';' + value
                if value:
                    SetValueEx(key, name, 0, REG_EXPAND_SZ, value)
                else:
                    DeleteValue(key, name)

            win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')

    finally:
        CloseKey(key)
        CloseKey(reg)


def query_value_win(key, name):
    value, type_id = QueryValueEx(key, name)
    return value

def show_win(key):
    for i in range(1024):
        try:
            n,v,t = EnumValue(key, i)
            print('%s=%s' % (n, v))
        except EnvironmentError:
            break