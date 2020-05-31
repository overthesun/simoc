import os
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
              "auth_secret": os.environ.get('AUTH_SECRET', ''),
              "public_ip": os.environ.get('PUBLIC_IP', '')}

    simoc_celery_cluster = j2_env.get_template('k8s/deployments/simoc_celery_cluster.yaml.jinja')
    simoc_flask_server = j2_env.get_template('k8s/deployments/simoc_flask_server.yaml.jinja')
    simoc_celery_autoscaler = j2_env.get_template('k8s/autoscalers/simoc_celery_autoscaler.yaml.jinja')
    simoc_flask_autoscaler = j2_env.get_template('k8s/autoscalers/simoc_flask_autoscaler.yaml.jinja')
    traefik = j2_env.get_template('k8s/ingresses/traefik.yaml.jinja')
    traefik_values = j2_env.get_template('k8s/ingresses/traefik_values.yaml.jinja')

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

