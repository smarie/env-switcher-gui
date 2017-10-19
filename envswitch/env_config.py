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

    def apply(self, whole_machine: bool=False):
        """
        Applies this environment on the OS

        :param whole_machine: a boolean indicating if we should apply to local user environment (False) or whole
        machine (True)
        :return:
        """
        target = 'WHOLE MACHINE' if whole_machine else 'CURRENT USER'
        print("Applying environment '" + self.name + "' (" + self.id + ") for " + target)
        set_env_variables_permanently(self.env_variables_dct, whole_machine=whole_machine)
        print("Applying environment DONE")


class UnknownEnvIdException(Exception):
    def __init__(self, msg):
        """
        There was once a bug with a test framework requiring this constructor to only have one argument, that's why we
        provide a static constructor below with `create_from`
        :param msg:
        """
        super(UnknownEnvIdException, self).__init__(msg)

    @staticmethod
    def create_from(env_id, available_envs_list):
        e = UnknownEnvIdException("Environment id '" + env_id + "' is unknown in this configuration file. Available "
                                  "environments: " + str(available_envs_list))
        e.env_id = env_id
        e.available_envs = available_envs_list
        return e


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

    def get_available_envs(self):
        """

        :return: the list of available environments
        """
        return list(self.envs.keys())

    def apply(self, env_id, whole_machine: bool = False):
        """
        Applies environment 'id', or throws an error if that environment id does not exist

        :param env_id: the environment id to apply
        :param whole_machine: a boolean indicating if we should apply to local user environment (False) or whole
        machine (True)
        :return:
        """
        # if the environment required is known, apply it
        if env_id in self.envs.keys():
            self.envs[env_id].apply(whole_machine=whole_machine)
        else:
            raise UnknownEnvIdException.create_from(env_id, list(self.envs.keys()))

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
