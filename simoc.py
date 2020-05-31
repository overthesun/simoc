"""
Script to install, start, stop, reset, etc. SIMOC through docker-compose.
"""

import os
import sys
import time
import socket
import pathlib
import argparse
import subprocess

ENV_FILE = 'simoc_docker.env'
COMPOSE_FILE = 'docker-compose.mysql.yml'
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

COMMANDS = {}
def cmd(func):
    COMMANDS[func.__name__] = func
    return func

def run(args):
    print('>'*80)
    print(' '.join(args))
    print('-'*80)
    env = {**os.environ, **ENVVARS}  # add original env
    result = subprocess.run(args, env=env)
    print('-'*80)
    print(result)
    print('<'*80)
    print()
    return result

def docker_compose(*args):
    return run([*DOCKER_COMPOSE_CMD, *args])

@cmd
def print_env():
    """Print a copy-pastable list of envvars."""
    for key, value in ENVVARS.items():
        print(f'export {key}={value!r}')
    return True

@cmd
def generate_scripts():
    """Generate simoc_nginx.conf and docker-compose.mysql.yml."""
    from jinja2 import Environment, FileSystemLoader
    j2_env = Environment(loader=FileSystemLoader('./'),
                         trim_blocks=True, lstrip_blocks=True)
    config = {
        "server_name": ENVVARS.get('SERVER_NAME', 'localhost'),
        "use_ssl": int(ENVVARS.get('USE_SSL', False)),
        "http_port": ENVVARS.get('HTTP_PORT', 8000),
        "https_port": ENVVARS.get('HTTPS_PORT', 8443),
        "use_certbot": int(ENVVARS.get('USE_CERTBOT', False)),
        "redirect_to_ssl": int(ENVVARS.get('REDIRECT_TO_SSL', False)),
        "add_basic_auth": int(ENVVARS.get('ADD_BASIC_AUTH', False)),
        "valid_referers": ENVVARS.get('VALID_REFERERS', '')
    }
    nginx_conf = j2_env.get_template('nginx/simoc_nginx.conf.jinja')
    docker_compose = j2_env.get_template('docker-compose.mysql.yml.jinja')
    print('Generating scripts:')
    with open('./nginx/simoc_nginx.conf', 'w') as f:
        f.write(nginx_conf.render(**config))
        print('  * nginx/simoc_nginx.conf created')
    with open('docker-compose.mysql.yml', 'w') as f:
        f.write(docker_compose.render(**config))
        print('  * docker-compose.mysql.yml created')
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
def build():
    """Build the docker container."""
    return docker_compose('build')

@cmd
def start_services():
    """Starts the services."""
    return docker_compose('up', '-d',
                          '--force-recreate',
                          '--scale', f'celery-worker={CELERY_WORKERS}',
                          '--scale', f'flask-app={FLASK_WORKERS}')
@cmd
def init_db():
    """Initialize the MySQL DB."""
    attempts = 15
    for attempt in range(15):
        result = docker_compose('exec', 'celery-worker', 'python3', 'create_db.py')
        if result.returncode == 0:
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

@cmd
def remove_db():
    """Remove the volume for the MySQL DB."""
    return (docker_compose('rm', '--stop', '-v', 'simoc-db') and
            run(['docker', 'volume', 'rm', 'simoc_db-data']))

@cmd
def reset_db():
    """Remove and recreate the MySQL DB."""
    return (remove_db() and
            docker_compose('up', '-d', '--force-recreate', 'simoc-db'))

@cmd
def ps():
    """Run `docker-compose ps`."""
    return docker_compose('ps')
@cmd
def start():
    """Run `docker-compose start`."""
    return docker_compose('start')
@cmd
def restart():
    """Run `docker-compose restart`."""
    return docker_compose('restart')
@cmd
def stop():
    """Run `docker-compose stop`."""
    return docker_compose('stop')
@cmd
def logs():
    """Show all logs."""
    return docker_compose('logs', '-t', '-f')
@cmd
def celery_logs():
    """Show the celery logs."""
    return docker_compose('logs', '-t', '-f', 'celery-worker')
@cmd
def flask_logs():
    """Show the flask logs."""
    return docker_compose('logs', '-t', '-f', 'flask-app')
@cmd
def remove():
    """Remove all images and volumes."""
    return docker_compose('down', '--rmi', 'all', '--volumes')


@cmd
def setup():
    """Run a complete setup of SIMOC."""
    return (generate_scripts() and make_cert() and
            build() and start_services() and init_db())
@cmd
def rebuild():
    """Stop, rebuild, and restart the containers."""
    return stop() and build() and start_services()
@cmd
def hard_reset():
    """Stop and remove everything, then run a full setup."""
    return stop() and remove() and remove_db() and setup()


def create_help(cmds):
    help = ['Full list of available commands:']
    for cmd, func in cmds.items():
        help.append(f'{cmd.replace("_", "-"):18} {func.__doc__}')
    return '\n'.join(help)

if __name__ == '__main__':
    desc = """\
Simplify installation and maintainment of SIMOC.

Use `setup` to install SIMOC, `rebuild` to rebuild the containers.
Use `hard-reset` to remove and reinstall everything.
Use `start`, `stop`, `restart` to control the containers.
Use `logs`, `celery-logs`, `flask-logs`, to see the logs.
"""
    parser = argparse.ArgumentParser(
        description=desc,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--docker-file', metavar='FILE',
                        help='the docker-compose yml file (default: %(default)r)',
                        default=COMPOSE_FILE)
    parser.add_argument('cmd', metavar='CMD', help=create_help(COMMANDS))
    args = parser.parse_args()

    if args.docker_file:
        COMPOSE_FILE = args.docker_file
        DOCKER_COMPOSE_CMD = ['docker-compose', '-f', COMPOSE_FILE]

    cmd = args.cmd.replace('-', '_')
    if cmd in COMMANDS:
        result = COMMANDS[cmd]()
        parser.exit(getattr(result, 'returncode', 0))
    else:
        cmds = ', '.join(cmd.replace('_', '-') for cmd in COMMANDS.keys())
        parser.exit(f'Command not found.  Available commands: {cmds}')
