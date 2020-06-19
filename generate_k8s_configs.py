import os
import subprocess
import json
from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    j2_env = Environment(loader=FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)

    config = {"gcp_project_id": os.environ.get('GCP_PROJECT_ID', ''),
              "gcp_zone": os.environ.get('GCP_ZONE', ''),
              "gcp_region": os.environ.get('GCP_REGION', ''),
              "min_flask_replicas": os.environ.get('MIN_FLASK_REPLICAS', ''),
              "max_flask_replicas": os.environ.get('MAX_FLASK_REPLICAS', ''),
              "min_celery_replicas": os.environ.get('MIN_CELERY_REPLICAS', ''),
              "max_celery_replicas": os.environ.get('MAX_CELERY_REPLICAS', ''),
              "server_name": os.environ.get('SERVER_NAME', ''),
              "acme_email": os.environ.get('ACME_EMAIL', ''),
              "acme_staging": int(os.environ.get('ACME_STAGING', True)),
              "basic_auth": int(os.environ.get('BASIC_AUTH', False)),
              "auth_username": os.environ.get('AUTH_USERNAME', ''),
              "auth_password": os.environ.get('AUTH_PASSWORD', ''),
              "static_ip_name": os.environ.get('STATIC_IP_NAME', ''),
              "redis_host": os.environ.get('REDIS_HOST', ''),
              "redis_port": os.environ.get('REDIS_PORT', ''),
              "redis_use_password": int(os.environ.get('REDIS_USE_PASSWORD', False)),
              "db_host": os.environ.get('DB_HOST', ''),
              "db_port": os.environ.get('DB_PORT', ''),
              "db_user": os.environ.get('DB_USER', ''),
              "db_name": os.environ.get('DB_NAME', '')}

    redis_environment = j2_env.get_template('k8s/deployments/redis_environment.yaml.jinja')
    simoc_db_environment = j2_env.get_template('k8s/deployments/simoc_db_environment.yaml.jinja')
    simoc_celery_cluster = j2_env.get_template('k8s/deployments/simoc_celery_cluster.yaml.jinja')
    simoc_flask_server = j2_env.get_template('k8s/deployments/simoc_flask_server.yaml.jinja')
    simoc_celery_autoscaler = j2_env.get_template('k8s/autoscalers/simoc_celery_autoscaler.yaml.jinja')
    simoc_flask_autoscaler = j2_env.get_template('k8s/autoscalers/simoc_flask_autoscaler.yaml.jinja')
    traefik = j2_env.get_template('k8s/ingresses/traefik.yaml.jinja')
    traefik_values = j2_env.get_template('k8s/ingresses/traefik_values.yaml.jinja')

    gcloud_cmd = f"gcloud compute addresses describe {config['static_ip_name']} --region {config['gcp_region']} --format=json".split()
    result = subprocess.run(gcloud_cmd, capture_output=True)
    config['public_ip'] = json.loads(result.stdout.decode('utf-8'))['address']

    if config['basic_auth']:
        htpasswd_cmd = f"htpasswd -nb {config['auth_username']} {config['auth_password']} | base64"
        result = subprocess.Popen(htpasswd_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        config['auth_secret'] = result.communicate()[0].decode('utf-8').strip()

    with open('k8s/deployments/redis_environment.yaml', 'w') as f:
        f.write(redis_environment.render(**config))
    with open('k8s/deployments/simoc_db_environment.yaml', 'w') as f:
        f.write(simoc_db_environment.render(**config))
    with open('k8s/deployments/simoc_celery_cluster.yaml', 'w') as f:
        f.write(simoc_celery_cluster.render(**config))
    with open('k8s/deployments/simoc_flask_server.yaml', 'w') as f:
        f.write(simoc_flask_server.render(**config))
    with open('k8s/autoscalers/simoc_celery_autoscaler.yaml', 'w') as f:
        f.write(simoc_celery_autoscaler.render(**config))
    with open('k8s/autoscalers/simoc_flask_autoscaler.yaml', 'w') as f:
        f.write(simoc_flask_autoscaler.render(**config))
    with open('k8s/ingresses/traefik.yaml', 'w') as f:
        f.write(traefik.render(**config))
    with open('k8s/ingresses/traefik_values.yaml', 'w') as f:
        f.write(traefik_values.render(**config))

