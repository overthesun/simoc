"""
Script to install, start, stop, reset, etc. SIMOC through docker-compose.
"""

import os
import sys
import time
import json
import socket
import pathlib
import argparse
import subprocess

import generate_docker_configs

ENV_FILE = 'simoc_docker.env'
AGENT_DESC = 'agent_desc.json'

COMPOSE_FILE = 'docker-compose.mysql.yml'
DEV_FE_COMPOSE_FILE = 'docker-compose.dev-fe.yml'
DEV_BE_COMPOSE_FILE = 'docker-compose.dev-be.yml'
AGENT_DESC_COMPOSE_FILE = 'docker-compose.agent-desc.yml'
DOCKER_COMPOSE_CMD = ['docker-compose', '-f', COMPOSE_FILE]


def parse_env(fname):
    env = {}
    with open(fname) as f:
        for line in map(str.strip, f):
            if not line or line.startswith('#'):
                continue
            if line.startswith('export'):
                key, value = line.split(None, 1)[1].split('=', 1)
                env[key] = value.strip('"\'')
            else:
                print(f'Unrecognized line in {fname}: {line!r}')
    return env

try:
    ENVVARS = parse_env(ENV_FILE)
except FileNotFoundError:
    sys.exit(f"Can't find env file: {ENV_FILE!r}")

FLASK_WORKERS = ENVVARS['FLASK_WORKERS']
CELERY_WORKERS = ENVVARS['CELERY_WORKERS']

# update environ with the new envvars
os.environ.update(ENVVARS)

# if the docker-compose file is missing, create it
if not pathlib.Path(COMPOSE_FILE).exists():
    generate_docker_configs.main()


COMMANDS = {}

def cmd(func):
    """Decorator to add commands to the COMMANDS dict."""
    COMMANDS[func.__name__] = func
    return func

def run(args):
    print('>'*80)
    print(' '.join(args))
    print('-'*80)
    result = subprocess.run(args, env=os.environ)
    print('-'*80)
    print(result)
    print('<'*80)
    print()
    return not result.returncode

@cmd
def docker_compose(*args):
    """Run an arbitrary docker-compose command."""
    return run([*DOCKER_COMPOSE_CMD, *args])

@cmd
def print_env():
    """Print a copy-pastable list of envvars."""
    for key, value in ENVVARS.items():
        print(f'export {key}={value!r}')
    return True


# initial setup
@cmd
def generate_scripts():
    """Generate simoc_nginx.conf and docker-compose.mysql.yml."""
    generate_docker_configs.main()
    print()
    return True

@cmd
def make_cert():
    """Create the certs/cert.pem SSL certificate."""
    pathlib.Path('certs').mkdir(exist_ok=True)
    #print('Creating SSL certificates.  Use the following values:',
          #'Country Name (2 letter code) []:US',
          #'State or Province Name (full name) []:Texas',
          #'Locality Name (eg, city) []:Austin',
          #'Organization Name (eg, company) []:SIMOC',
          #'Organizational Unit Name (eg, section) []:',
          #f'Common Name (eg, fully qualified host name) []:{domain}',
          #'Email Address []:', sep='\n')
    certpath = 'certs/cert.pem'
    if socket.gethostname().endswith('simoc.space'):
        domain = 'beta.simoc.space'
    else:
        domain = 'localhost'
    return run(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
                '-out', certpath, '-keyout', 'certs/key.pem', '-days', '365',
                '-subj', f"/C=US/ST=Texas/L=Austin/O=SIMOC/CN={domain}"])

@cmd
def build_images():
    """Build the flask and celery images locally."""
    return (run(['docker', 'build', '-t', 'simoc_flask', '.']) and
            run(['docker', 'build', '-f', 'Dockerfile-celery-worker',
                 '-t', 'simoc_celery', '.']))

@cmd
def start_services():
    """Starts the services."""
    return docker_compose('up', '-d',
                          '--force-recreate',
                          '--scale', f'celery-worker={CELERY_WORKERS}',
                          '--scale', f'flask-app={FLASK_WORKERS}')

# DB
@cmd
def init_db():
    """Initialize the MySQL DB."""
    print('Creating DB.  This might take a while...\n')
    attempts = 15
    for attempt in range(15):
        result = docker_compose('exec', 'celery-worker', 'python3', 'create_db.py')
        if result is True:
            return result
        else:
            print('create_db.py failed: if the error above says:\n'
                  '  "Can\'t connect to MySQL server on \'simoc-db\' (111)"\n'
                  'this is expected -- it might take a few minutes before the '
                  'db is up and running. Another attempt will be made in 15s.\n')
            time.sleep(15)
    else:
        print(f'Giving up after {attempts} attempts.  Run the above command '
              f'manually to try again.')
    return False

@cmd
def remove_db():
    """Remove the volume for the MySQL DB."""
    docker_compose('rm', '--stop', '-v', '-f', 'simoc-db')
    run(['docker', 'volume', 'rm', 'simoc_db-data'])
    return True  # the volume rm might return False if the volume is missing


@cmd
def reset_db():
    """Remove and recreate the MySQL DB."""
    # the up is needed to update the simoc source code
    # in the containers before rebuilding the db,
    # restarting nginx is needed to make sure the
    # ips of the flask/celery containers are updated
    return (up() and restart('nginx') and remove_db() and
            docker_compose('up', '-d', '--force-recreate', 'simoc-db') and
            init_db())


# start/stop
@cmd
def up(*args):
    """Start/update the containers with `docker-compose up -d`."""
    return docker_compose('up', '-d', *args)

@cmd
def down(*args):
    """Stop/remove the containers with `docker-compose down`."""
    return docker_compose('down', *args)

@cmd
def restart(*args):
    """Restart the containers with `docker-compose restart`."""
    return docker_compose('restart', *args)


# status and logging
@cmd
def ps(*args):
    """Run `docker-compose ps`."""
    return docker_compose('ps', *args)

@cmd
def logs(*args):
    """Show all logs."""
    return docker_compose('logs', '-t', '-f', *args)

@cmd
def celery_logs():
    """Show the celery logs."""
    return docker_compose('logs', '-t', '-f', 'celery-worker')

@cmd
def flask_logs():
    """Show the flask logs."""
    return docker_compose('logs', '-t', '-f', 'flask-app')


# install/uninstall
@cmd
def setup():
    """Run a complete setup of SIMOC."""
    return (generate_scripts() and make_cert() and build_images() and
            start_services() and init_db() and ps())

@cmd
def teardown():
    """Remove simoc and all related containers/images/volumes"""
    return docker_compose('down', '--rmi', 'all',
                          '--volumes', '--remove-orphans')

@cmd
def reset():
    """Remove everything, then run a full setup."""
    return teardown() and setup()


# debugging/testing
@cmd
def shell(container):
    """Run an interactive shell in the specified container."""
    return docker_compose('exec', container, '/bin/bash')

# others
@cmd
def format_agent_desc(fname=AGENT_DESC):
    """Reformat agent_desc.json files (e.g. the one generated by ACE)."""
    print(f'Reformatting <{fname}>...', end=' ')
    with open(fname) as f:
        ad = json.load(f)
    with open(fname, 'w', newline='\r\n') as f:
        json.dump(ad, f, indent=2)
    print('done.')



def create_help(cmds):
    help = ['Full list of available commands:']
    for cmd, func in cmds.items():
        help.append(f'{cmd.replace("_", "-"):18} {func.__doc__}')
    return '\n'.join(help)


if __name__ == '__main__':
    desc = """\
Simplify installation and maintainment of SIMOC.

Use `setup` to install SIMOC, `teardown` to uninstall everything.
Use `reset` to reinstall (same as `teardown` + `setup`).
Use `up` to start/update the containers, `down` to stop/remove them.
Use `logs`, `flask-logs`, `celery-logs`, to see the logs.
Use the `--with-dev-backend` flag to run the dev backend container.
"""
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--docker-file', metavar='FILE', default=COMPOSE_FILE,
        help='the docker-compose yml file (default: %(default)r)'
    )
    parser.add_argument(
        '--with-dev-frontend', action='store_true',
        help='also start the dev frontend container'
    )
    parser.add_argument(
        '--dev-frontend-yml', metavar='FILE',
        help='the dev frontend docker-compose yml file'
    )
    parser.add_argument(
        '--dev-frontend-dir', metavar='DIR',
        help='the dir where the dev frontend code is'
    )
    parser.add_argument(
        '--with-dev-backend', action='store_true',
        help='use the dev backend flask container'
    )
    parser.add_argument(
        '--dev-backend-yml', metavar='FILE',
        help='the dev backend docker-compose yml file'
    )
    parser.add_argument(
        '--agent-desc', metavar='FILE',
        help='the agent_desc.json file to be used'
    )
    parser.add_argument('cmd', metavar='CMD', help=create_help(COMMANDS))
    parser.add_argument('args', metavar='*ARGS', nargs='*',
                        help='Additional optional args to be passed to CMD.')
    args = parser.parse_args()

    if args.docker_file:
        COMPOSE_FILE = args.docker_file
        DOCKER_COMPOSE_CMD = ['docker-compose', '-f', COMPOSE_FILE]

    if (args.dev_frontend_dir or args.dev_frontend_yml) and not args.with_dev_frontend:
        parser.error("Can't specify the dev frontend dir/yml without --with-dev-frontend")

    if args.dev_backend_yml and not args.with_dev_backend:
        parser.error("Can't specify the dev backend yml without --with-dev-backend")

    if args.with_dev_frontend:
        if args.dev_frontend_dir:
            os.environ['DEV_FE_DIR'] = args.dev_frontend_dir
        if not os.environ['DEV_FE_DIR']:
            parser.error('Please specify the dev frontend dir (either in '
                         'simoc_docker.env or with --dev-frontend-dir).')
        yml_file = args.dev_frontend_yml or DEV_FE_COMPOSE_FILE
        DOCKER_COMPOSE_CMD.extend(['-f', yml_file])

    if args.with_dev_backend:
        yml_file = args.dev_backend_yml or DEV_BE_COMPOSE_FILE
        DOCKER_COMPOSE_CMD.extend(['-f', yml_file])

    if args.agent_desc and args.with_dev_backend:
        parser.error("Can't specify the agent_desc.json file with --with-dev-backend")

    if args.agent_desc:
        os.environ['AGENT_DESC'] = str(pathlib.Path(args.agent_desc).resolve())
        DOCKER_COMPOSE_CMD.extend(['-f', AGENT_DESC_COMPOSE_FILE])

    cmd = args.cmd.replace('-', '_')
    if cmd in COMMANDS:
        result = COMMANDS[cmd](*args.args)
        parser.exit(not result)
    else:
        cmds = ', '.join(cmd.replace('_', '-') for cmd in COMMANDS.keys())
        parser.error(f'Command not found.  Available commands: {cmds}')
