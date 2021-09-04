==============================================
Deploy SIMOC to Google Kubernetes Engine (GKE)
==============================================

1. Configure a new ``GCP`` Project
==================================

Login to the `Cloud Console <https://cloud.google.com/>`_.

Create or select a `GCP Project
<https://cloud.google.com/resource-manager/docs/creating-managing-projects>`_.

Make sure that `billing is enabled for your project
<https://cloud.google.com/billing/docs/how-to/modify-project>`_.

Navigate to the `API Library
<https://console.cloud.google.com/apis/library>`_.

Activate the following GCP APIs:

* Compute Engine API
* Kubernetes Engine API
* Google Container Registry API
* Cloud SQL (optional)
* Google Cloud Memorystore for Redis API (optional)

Set up managed database backends (optional).  ``SIMOC`` supports
multiple scenarios for hosting  ``MySQL`` and ``Redis`` components on GCP:

1. Using database instances fully managed by GCP (zero maintenance,
   provisioning, operations)
2. Manually deploying DB components to a ``Kubernetes`` cluster
   (native k8s automations - health checks, recovery, auto scaling)

Follow the official ``Google Cloud`` instructions to set up managed
database components:

* https://cloud.google.com/memorystore/docs/redis/creating-managing-instances#console
* https://cloud.google.com/sql/docs/mysql/create-instance#console

Make sure that you configured MySQL version ``5.7+`` and Redis ``5.0+``.

Copy the IP addresses that ``GCP`` provisioned for the corresponding
instance and the ``MySQL`` password as you will need those values later on.

Initialize a new ``Cloud Shell`` session:

* https://console.cloud.google.com/getting-started
* https://cloud.google.com/shell/docs/quickstart
* https://console.cloud.google.com/cloudshell

Enable `Boost mode
<https://cloud.google.com/shell/docs/how-cloud-shell-works#boost_mode>`_
in ``Cloud Shell``.


2. Configure ``SIMOC`` deployment
=================================

Make sure you logged in and retrieved the ``GCP`` credentials::

    gcloud auth login
    gcloud auth application-default login

Configure ``SSH`` access for ``GitHub`` and
generate a new ``SSH`` key (``use empty passphrase``)::

    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

Copy the content of the ``id_rsa.pub`` file to your clipboard::

    cat ~/.ssh/id_rsa.pub

Use the following guide starting from the ``Step 2``
to add the SSH key to your GitHub account:
https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

Clone ``SIMOC`` code from ``GitHub``::

    cd ~/
    git clone git@github.com:overthesun/simoc.git
    cd simoc/


Open the ``simoc_k8s.env`` file with any text editor::

    vim simoc_k8s.env

Update the following variables in the default deployment configuration:

* ``GCP_PROJECT_ID`` - string ID of the GCP project (execute ``gcloud projects list`` to get all available options)
* ``GCP_ZONE`` - GCP regional zone to deploy all SIMOC resources (execute ``gcloud compute zones list`` to get all available options)
* ``K8S_CLUSTER_NAME`` - string name for the Kubernetes cluster
* ``K8S_MIN_NODES`` - minimum number of nodes in the cluster
* ``K8S_MAX_NODES`` - maximum number of nodes in the cluster (auto-scaling)
* ``MIN_FLASK_REPLICAS`` - minimum number of Flask worker containers
* ``MAX_FLASK_REPLICAS`` - maximum number of Flask worker containers (auto-scaling)
* ``MIN_CELERY_REPLICAS`` - minimum number of Celery worker containers
* ``MAX_CELERY_REPLICAS`` - maximum number of Celery worker containers (auto-scaling)
* ``SERVER_NAME`` - DNS hostname for the SIMOC application
* ``ACME_EMAIL`` - email address for the SSL certificate from LetsEncrypt
* ``ACME_STAGING`` - ``1`` to use testing LetsEncrypt servers, ``0`` to use production servers instead (default: ``1``)
* ``BASIC_AUTH`` - ``1`` to use Basic HTTP Authentication (default: ``0``)
* ``AUTH_USERNAME`` - username for Basic Auth
* ``AUTH_PASSWORD`` - password for Basic Auth
* ``STATIC_IP_NAME`` - string name for a static external IP address
* ``REDIS_HOST`` - domain or IP address of the Redis database (do not change the default value if you DON"T plan to use a managed database)
* ``REDIS_PORT`` - Redis TCP port (default: ``6379``)
* ``REDIS_USE_PASSWORD`` - ``0`` to use password auth in Redis (default: ``1``, use ``0`` if you DO plan to use a managed database)
* ``DB_HOST`` - domain or IP address of the MySQL database (do not change the default value if you DON"T plan to use a managed database)
* ``DB_PORT`` - MySQL TCP port (default: ``3306``)
* ``DB_USER`` - MySQL username (default: ``root``)
* ``DB_NAME`` - MySQL database name (default: ``simoc``)

::

    export GCP_PROJECT_ID=simoc-gcp-180321
    export GCP_ZONE=us-east1-b
    export K8S_CLUSTER_NAME=simoc-cluster
    export K8S_MIN_NODES=1
    export K8S_MAX_NODES=2
    export MIN_FLASK_REPLICAS=2
    export MAX_FLASK_REPLICAS=4
    export MIN_CELERY_REPLICAS=2
    export MAX_CELERY_REPLICAS=4
    export SERVER_NAME=www.example.com
    export ACME_EMAIL=admin@example.com
    export ACME_STAGING=1
    export BASIC_AUTH=1
    export AUTH_USERNAME=admin
    export AUTH_PASSWORD=password
    export STATIC_IP_NAME=simoc-static-ip
    export REDIS_HOST=redis-master.default.svc.cluster.local
    export REDIS_PORT=6379
    export REDIS_USE_PASSWORD=1
    export DB_HOST=simoc-db-mysql.default.svc.cluster.local
    export DB_PORT=3306
    export DB_USER=root
    export DB_NAME=simoc

Load ``SIMOC`` configuration into the shell environment::

    source simoc_k8s.env

Configure ``GCP Project`` and ``Zone``::

    gcloud config set project $GCP_PROJECT_ID
    gcloud config set compute/zone $GCP_ZONE


3. Build ``SIMOC`` images
=========================

Configure ``Docker`` environment::

    gcloud auth configure-docker

Build ``Docker`` images::

    docker build -t simoc_flask_mysql_k8s .
    docker build -f Dockerfile-celery-worker -t simoc_celery_worker_k8s .

Push images to ``Container Registry``::

    docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
    docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
    docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
    docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest


4. Create ``Kubernetes`` cluster
================================

::

    gcloud container clusters create $K8S_CLUSTER_NAME \
        --enable-ip-alias \
        --create-subnetwork="" \
        --network=default \
        --zone $GCP_ZONE \
        --preemptible \
        --machine-type=n1-standard-4 \
        --num-nodes $K8S_MIN_NODES \
        --min-nodes $K8S_MIN_NODES \
        --max-nodes $K8S_MAX_NODES \
        --enable-autoscaling


5. Deploy ``SIMOC`` to the cluster
==================================

Configure ``Kubernetes`` client (``kubctl``)::

    gcloud container clusters get-credentials $K8S_CLUSTER_NAME --zone $GCP_ZONE

Install ``Helm`` client (``package manager for k8s``)::

    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
    chmod 700 get_helm.sh
    ./get_helm.sh

Register ``Helm`` repositories::

    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add stable https://kubernetes-charts.storage.googleapis.com/
    helm repo add traefik https://containous.github.io/traefik-helm-chart
    helm repo update


Deploy custom database backends by following the instructions below
if you prefer to manually manage ``SIMOC`` database components:

* Deploy ``MySQL`` server component::

    helm install simoc-db \
        --set mysqlDatabase=simoc \
        --set resources.requests.cpu=1.0 \
        --set resources.requests.memory=512Mi \
        --set resources.limits.cpu=1.0 \
        --set resources.limits.memory=512Mi \
        stable/mysql

* Save ``MySQL`` credentials to ``Cloud Secrets``::

    export DB_PASSWORD=$(
        kubectl get secret --namespace default simoc-db-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode
        echo
    )
    kubectl create secret generic simoc-db-creds --from-literal=db_password=$DB_PASSWORD

* Deploy ``Redis`` server component::

    curl -Lo values-production.yaml https://raw.githubusercontent.com/bitnami/charts/master/bitnami/redis/values-production.yaml
    helm install redis bitnami/redis --values values-production.yaml

* Save ``Redis`` credentials to ``Cloud Secrets``::

    export REDIS_PASSWORD=$(
        kubectl get secret --namespace default redis -o jsonpath="{.data.redis-password}" | base64 --decode
        echo
    )
    kubectl create secret generic redis-creds --from-literal=redis_password=$REDIS_PASSWORD

Generate a ``Flask`` secret string and save it to ``Cloud Secrets``::

    export FLASK_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
    kubectl create secret generic flask-secret --from-literal=flask_secret=$FLASK_SECRET

Reserve a static IP address for ``SIMOC`` application::

    gcloud compute addresses create $STATIC_IP_NAME --region $GCP_REGION

Install ``apache2-utils`` if you plan to use ``Basic Auth`` (optional)::

    sudo apt-get install apache2-utils

Generate ``Kubernetes`` manifest files::

    python3 generate_k8s_configs.py


Deploy ``SIMOC`` backend to the ``Kubernetes`` cluster::

    kubectl apply -f k8s/deployments/redis_environment.yaml
    kubectl apply -f k8s/deployments/simoc_db_environment.yaml
    kubectl apply -f k8s/deployments/simoc_flask_server.yaml
    kubectl apply -f k8s/deployments/simoc_celery_cluster.yaml
    kubectl apply -f k8s/autoscalers/simoc_flask_autoscaler.yaml
    kubectl apply -f k8s/autoscalers/simoc_celery_autoscaler.yaml
    kubectl apply -f k8s/services/simoc_flask_service.yaml

Deploy ``Traefik`` router component::

    helm install traefik --values k8s/ingresses/traefik_values.yaml traefik/traefik
    kubectl applly -f k8s/ingresses/traefik.yaml
    kubectl patch deployment/traefik -p '{"spec": {"template": {"spec": {"initContainers": [{"name": "fix-acme", "image": "alpine:3.6", "command": ["chmod", "600", "/data/acme.json"], "volumeMounts": [{"name": "data", "mountPath": "/data"}]}]}}}}'


Initialize ``MySQL`` database by executing a remote command on
``simoc-flask-server`` container to initiate a database reset::

    kubectl exec \
        "$(kubectl get pods -l app=simoc-flask-server --output=jsonpath={.items..metadata.name} | cut -d  ' ' -f 1)" \
        -- bash -c "python3 create_db.py"


6. Performing rolling updates
=============================

Make sure you logged in and retrieved the ``GCP`` credentials::

    gcloud auth login
    gcloud auth application-default login

Load ``SIMOC`` configuration into the environment::

    source simoc_k8s.env

Configure ``GCP Project`` and ``Zone``::

    gcloud config set project $GCP_PROJECT_ID
    gcloud config set compute/zone $GCP_ZONE

Configure ``Kubernetes`` client (``kubctl``)::

    gcloud container clusters get-credentials $K8S_CLUSTER_NAME --zone $GCP_ZONE

Configure ``Docker`` environment::

    gcloud auth configure-docker

Re-build ``Docker`` images::

    docker build -t simoc_flask_mysql_k8s .
    docker build -f Dockerfile-celery-worker -t simoc_celery_worker_k8s .

Push new images to ``Container Registry``::

    docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
    docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
    docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
    docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest

Re-deploy ``SIMOC`` containers with new images::

    kubectl rollout restart deployment/simoc-flask-server
    kubectl rollout restart deployment/simoc-celery-cluster

Inspect the status of a rollout::

    kubectl rollout status deployment simoc-flask-server
    kubectl rollout status deployment simoc-celery-cluster


7. Useful commands
==================

Load ``SIMOC`` config into the shell environment::

    source simoc_k8s.env
    gcloud config set project $GCP_PROJECT_ID
    gcloud config set compute/zone $GCP_ZONE
    gcloud container clusters get-credentials $K8S_CLUSTER_NAME --zone $GCP_ZONE
    gcloud auth configure-docker


Display detailed information about a reserved IP address::

    gcloud compute addresses describe $STATIC_IP_NAME --region $GCP_REGION

Scale ``SIMOC`` components up and down independently

* Scale the number of ``Celery`` containers to ``20``::

    kubectl scale --replicas=20 -f k8s/deployments/simoc_celery_cluster.yaml

* Scale the number of ``Flask`` containers to ``5``::

    kubectl scale --replicas=5 -f k8s/deployments/simoc_flask_server.yaml


Stream logs from the ``flask-server`` service::

    kubectl logs -f -l app=simoc-flask-server --all-containers --max-log-requests 100


Stream logs from the ``celery-cluster`` service::

    kubectl logs -f -l app=simoc-celery-cluster --all-containers --max-log-requests 100


Stream logs from the ``traefik`` service::

    kubectl logs -f -l app.kubernetes.io/name=traefik --all-containers --max-log-requests 100

