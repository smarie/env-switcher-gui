import click
from envswitch.gui import main, _app_version


@click.command()
@click.version_option(version=_app_version)
@click.argument('env_id')
@click.option('--env_file', '-f', type=click.Path(exists=True),
              help='Uses the specified *.yml or *.yaml environment definition file instead of the last one opened in '
                   'the Envswitch GUI.')
def cli(env_id, env_file=None):
    """
    Sets all environment variables defined in environment ENV_ID, in a permanent manner (changes will persist once this
    command shell is closed).

    By default, the definition for environment ENV_ID is looked up in the last environment configuration file opened
    with the Envswitch GUI.

    Alternatively you may specify a different environment configuration file with --env_file or -f.
    """
    main(headless=True, env_id=env_id, config_file_path=env_file)


# cli.help = cli.help.replace('%VERSION%', _app_version)


if __name__ == '__main__':
    cli(prog_name='envswitch')
