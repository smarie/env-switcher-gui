import click

from envswitch.utils import get_version
from envswitch.gui import EnvSwitcherAppHeadless


@click.command()
@click.argument('env_id')
@click.option('--env_file', '-f', type=click.Path(exists=True),
              help='Uses the specified *.yml or *.yaml environment definition file instead of the last one opened in '
                   'the Envswitch GUI.')
def apply(env_id, env_file=None):
    """ see below for true help, this one disappears during cx_Freeze packaging """
    a = EnvSwitcherAppHeadless(config_file_path=env_file)
    try:
        a.get_current_config().apply(env_id)
    except Exception as e:
        print('**ERROR** ' + str(e))
        return
    print('**DONE**')


apply.help = "Applies environment ENV_ID: sets all environment variables defined in that environment, in a permanent " \
             "manner (changes will persist once this command shell is closed). \n\n" \
             "By default, the definition for environment ENV_ID is looked up in the last configuration " \
             "file opened with the Envswitch GUI. Alternatively you may specify a different configuration" \
             " file with --env_file or -f. \n\n" \
             "You may wish to use 'envswitch list' to get a list of environment ids available."


@click.command()
@click.option('--env_file', '-f', type=click.Path(exists=True),
              help='Uses the specified *.yml or *.yaml environment definition file instead of the last one opened in '
                   'the Envswitch GUI.')
def list(env_file=None):
    """ see below for true help, this one disappears during cx_Freeze packaging """
    a = EnvSwitcherAppHeadless(config_file_path=env_file)
    file_path = a.get_current_config_file_path()
    envs_list = a.get_current_config().get_available_envs()
    print("Environments available in '" + file_path + "': " + str(envs_list))


list.help = "Lists the environment ids available in the last loaded configuration file, or in a specific " \
            "configuration file indicated with the --env_file option"


@click.command()
@click.argument('env_file', type=click.Path(exists=True))
def open(env_file):
    """ see below for true help, this one disappears during cx_Freeze packaging """
    a = EnvSwitcherAppHeadless(config_file_path=env_file)
    a.persist_last_opened_file()


open.help = "Opens the specified *.yml or *.yaml environment definition file, so that it will be the default one " \
            "available the next time a command is executed or the next time the GUI is launched"


# Note: we have to explicitly list the commands here otherwise the cx-frozen version does not find them
@click.group(commands={'apply': apply, 'list': list, 'open': open}, no_args_is_help=True)
@click.version_option(version=get_version())
def cli():
    """ see below for true help, this one disappears during cx_Freeze packaging """
    print('*** ENVSWITCH <' + get_version() + '> ***')


cli.help = "Envswitch commandline. Use 'envswitch COMMAND --help' to get help on any specific command below."


if __name__ == '__main__':
    cli(prog_name='envswitch')
