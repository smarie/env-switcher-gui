from collections import OrderedDict
from copy import copy
from typing import Optional, Dict

import yaml
from autoclass import check_var
from envswitch.env_api import set_env_variables_permanently

from envswitch.yaml_ordered_dict import safe_load_ordered

_NAME = 'name'


class EnvConfig:
    """
    Represents the configuration for a single environment
    """
    def __init__(self, env_id: str, env_variables: Dict[str, str]):
        """
        Constructor with an environment id and variables
        :param env_id:
        :param env_variables:
        """
        # environment id
        check_var(env_id, var_types=str, var_name='environment id')
        self.id = env_id

        # environment variables list
        for env_var, env_var_val in env_variables.items():
            check_var(env_var, var_types=str, var_name='environment variable name')
            check_var(env_var_val, var_types=str, var_name='environment variable value')
        self.env_variables_dct = copy(env_variables)

        # the name is a special variable that should be removed from the list
        self.name = self.env_variables_dct.pop(_NAME) if _NAME in self.env_variables_dct else self.id

    def __repr__(self):
        return self.name + '[' + self.id + '] : ' + repr(self.env_variables_dct)

    def to_dict(self):
        """
        Returns a dictionary version of this environment's contents (not the id)
        :return:
        """
        dct = OrderedDict()
        dct[_NAME] = self.name
        dct.update(self.env_variables_dct)
        return dct

    def apply(self):
        """
        Applies this environment on the OS
        :return:
        """
        print("Applying environment '" + self.name + "' (" + self.id + ")")
        set_env_variables_permanently(self.env_variables_dct)
        print("Applying environment DONE")


class GlobalEnvsConfig:
    """
    Represents the configuration for all environments
    """

    def __init__(self, dct: Dict[str, Dict[str, Optional[str]]]):
        """
        Constructor with an initial dictionary of environments (key is id)
        :param dct:
        """
        self.envs = OrderedDict()

        for env_id, env_desc in dct.items():
            # create environment configuration
            cfg = EnvConfig(env_id, env_desc)
            self.envs[env_id] = cfg

    def __repr__(self):
        return repr(self.envs)

    def __eq__(self, other):
        if type(other) != GlobalEnvsConfig:
            return False
        else:
            return self.to_yaml() == other.to_yaml()

    def to_dict(self):
        """
        Returns a dictionary version of this configuration
        :return:
        """
        dct = OrderedDict()
        for env_id, env in self.envs.items():
            dct[env_id] = env.to_dict()

        return dct

    @staticmethod
    def from_yaml(file):
        """
        Loads a YAML configuration file in safe mode and checks that it has the correct structure by creating a
        corresponding configuration object.

        :param file:
        :return:
        """
        conf = safe_load_ordered(file)
        res = GlobalEnvsConfig(conf)

        # safety: make sure the result is an instance of GlobalEnvsConfig
        assert isinstance(res, GlobalEnvsConfig)

        return res

    def to_yaml(self, stream=None):
        """
        Dumps this configuration into a yaml str
        :return:
        """
        return yaml.dump(self.to_dict(), stream=stream)
