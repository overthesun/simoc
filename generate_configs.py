import os
from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    j2_env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
    config = {"server_name":     os.environ.get('SERVER_NAME', 'localhost'),
              "use_ssl":         os.environ.get('USE_SSL', False),
              "http_port":       os.environ.get('HTTP_PORT', 8000),
              "https_port":      os.environ.get('HTTPS_PORT', 8443),
              "use_certbot":     os.environ.get('USE_CERTBOT', False),
              "redirect_to_ssl": os.environ.get('REDIRECT_TO_SSL', False),
              "add_basic_auth":  os.environ.get('ADD_BASIC_AUTH', False),
              "valid_referers":  os.environ.get('VALID_REFERERS', False)}
    nginx_conf = j2_env.get_template('nginx/simoc_nginx.conf.jinja')
    docker_compose = j2_env.get_template('docker-compose.mysql.yml.jinja')
    with open('./nginx/simoc_nginx.conf', 'w') as f:
        f.write(nginx_conf.render(**config))
    with open('docker-compose.mysql.yml', 'w') as f:
        f.write(docker_compose.render(**config))

