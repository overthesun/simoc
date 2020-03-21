# Deploy `SIMOC` to `Google Kubernetes Engine` (`MySQL` backend)

## Introduction
This guide describes the process of deploying `SIMOC` web application to the `Google Cloud Platform (GCP)` through the following set of steps:
1. Creating a new `GCP` project
2. Setting up the environment
3. Connecting to the `SIMOC` `GitHub` repository
4. Building `SIMOC` docker images
5. Spinning up a `Kubernetes` cluster
6. Deploying a `SIMOC` application to the cluster
7. Accessing the `SIMOC` application

## Configure a `GCP` Project

### Login to the `Cloud Console`
* https://cloud.google.com/

### Create or select a `GCP` project
* https://cloud.google.com/resource-manager/docs/creating-managing-projects

### Make sure that billing is enabled for your project
* https://cloud.google.com/billing/docs/how-to/modify-project

### Navigate to the API Library
* https://console.cloud.google.com/apis/library

### Activate the following APIs
* Compute Engine API
* Kubernetes Engine API
* Google Container Registry API

## Deploy `SIMOC` (using `Cloud Shell`)

### Initialize a new `Cloud Shell` session
* https://console.cloud.google.com/getting-started
* https://cloud.google.com/shell/docs/quickstart
* https://console.cloud.google.com/cloudshell

### Configure `GCP` Project and Zone

Make sure you logged in and retrieved the application credentials:
```bash
gcloud auth login
gcloud auth application-default login
```

Check the current configuration:
```bash
gcloud config list
```
Select the `Project` and the `Compute Zone` for the deployment:
```bash
gcloud projects list
gcloud compute zones list
```
```bash
export GCP_PROJECT_ID=<PROJECT_ID>
export GCP_ZONE=<GCP_ZONE>
```

Set up `Project` and `Zone` config:
```bash
gcloud config set project $GCP_PROJECT_ID
gcloud config set compute/zone $GCP_ZONE
```
Please note your selection as you will need those values later on in this guide.

### Install `Helm` client tool (`package manager for k8s`)
```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```

### Register `Helm` repositories
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
helm repo update
```

### Configure `GitHub` `SSH` access

Generate a new `SSH` key (`use empty passphrase`):
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Copy the content of the `id_rsa.pub` file to your clipboard:
```bash
cat ~/.ssh/id_rsa.pub
```

Use the following guide starting from the `Step 2` to add the SSH key to your GitHub account:
* https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

### Clone the `SIMOC` code from `GitHub`

```bash
cd ~/
git clone git@github.com:kstaats/simoc.git
cd simoc/
```

### Build `SIMOC` images

#### Configure a `Docker` environment
```bash
gcloud auth configure-docker
```

#### Build a `simoc_flask_mysql_k8s` image
```bash
docker build -t simoc_flask_mysql_k8s .
```

#### Build a `simoc_celery_worker_k8s` image
```bash
docker build -f celery_worker/Dockerfile -t simoc_celery_worker_k8s .
```

#### Push images to the `Container Registry`
```bash
docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
```

### Set up a `Kubernetes` cluster

#### Create a `Kubernetes` cluster
```bash
gcloud container clusters create k0 \
    --enable-ip-alias \
    --create-subnetwork="" \
    --network=default \
    --zone $GCP_ZONE \
    --preemptible \
    --machine-type=n1-standard-4 \
    --num-nodes 3 --enable-autoscaling --min-nodes 3 --max-nodes 10
```

#### Set up a `Kubernetes` environment
```bash
gcloud container clusters get-credentials k0 --zone $GCP_ZONE
```

### Deploy `SIMOC` to the `Kubernetes` cluster

#### Deploy `MySQL` server
```bash
helm install simoc-db \
    --set mysqlDatabase=simoc \
    --set resources.requests.cpu=1.0 \
    --set resources.requests.memory=512Mi \
    --set resources.limits.cpu=1.0 \
    --set resources.limits.memory=512Mi \
    stable/mysql
```

#### Save `MySQL` credentials to the `Cloud Secrets`
```bash
export DB_PASSWORD=$(
    kubectl get secret --namespace default simoc-db-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode
    echo
)
kubectl create secret generic simoc-db-creds \
    --from-literal=db_password=$DB_PASSWORD
```

#### Deploy `Redis` server
```bash
helm install redis bitnami/redis
```

#### Save `Redis` credentials to the `Cloud Secrets`
```bash
export REDIS_PASSWORD=$(
    kubectl get secret --namespace default redis -o jsonpath="{.data.redis-password}" | base64 --decode
    echo
)
kubectl create secret generic redis-creds \
    --from-literal=redis_password=$REDIS_PASSWORD
```

#### Configure and save the `Flask` secret string to the `Cloud Secrets`
```bash
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'
kubectl create secret generic flask-secret \
    --from-literal=flask_secret=$FLASK_SECRET
```

#### Create a static public IP address for the `SIMOC` application
```bash
gcloud compute addresses create simoc-static-ip --global
```

#### Update `Kubernetes` manifests
- Access the `Code Editor` from the toolbar by clicking on the pencil icon:
https://cloud.google.com/shell/docs/features#code_editor

- Open the `~/simoc/k8s/deployments/simoc_flask_server.yaml` file and fill in the `<PROJECT_ID>` value in the `spec/spec/containers/image` section:
```yaml
image: gcr.io/<PROJECT_ID>/simoc:latest
```

- Repeat the same for the `~/simoc/k8s/deployments/simoc_celery_cluster.yaml` file

- Open the `~/simoc/k8s/ingresses/managed_certificate.yaml` file and fill in the `<DOMAIN_NAME>` value in the `spec/domains` section:
```yaml
domains:
  - <DOMAIN_NAME>
```

#### Deploy the `SIMOC` backend into the cluster
```bash
kubectl create -f k8s/deployments/redis_environment.yaml
kubectl create -f k8s/deployments/simoc_db_environment.yaml
kubectl create -f k8s/deployments/simoc_flask_server.yaml
kubectl create -f k8s/deployments/simoc_celery_cluster.yaml
kubectl create -f k8s/autoscalers/simoc_flask_autoscaler.yaml
kubectl create -f k8s/autoscalers/simoc_celery_autoscaler.yaml
kubectl create -f k8s/ingresses/managed_certificate.yaml
kubectl create -f k8s/ingresses/simoc_backend_config.yaml
kubectl create -f k8s/services/simoc_flask_service.yaml
kubectl create -f k8s/ingresses/simoc_flask_ingress.yaml
```

#### Initialize a `MySQL` database
Execute a remote command on `simoc-flask-server` container to initiate a database reset:
```bash
kubectl exec \
    "$(kubectl get pods -l app=simoc-flask-server --output=jsonpath={.items..metadata.name} | cut -d  ' ' -f 1)" \
    -- bash -c "python3 create_db.py"
```

If the following error occurs, wait for 1-2 minutes and retry:
```
error: unable to upgrade connection: container not found ("simoc-flask-server")
```

#### Scale `SIMOC` components (optional)
Scale the number of `celery-worker` containers to `20`:
```bash
kubectl scale --replicas=20 -f k8s/deployments/simoc_celery_cluster.yaml
```

### Access the `SIMOC` web application
In `Cloud Console`, navigate to the `Kubernetes Engine -> Services & Ingress` tab:
* https://console.cloud.google.com/kubernetes/discovery

Once the cluster is up and running (may need to click a `Refresh` button), the `simoc-flask-ingress` service will list the HTTP/HTTPS Endpoints that you can use to access the app.

## Rollout updates


### Re-build a `simoc_flask_mysql_k8s` image
```bash
docker build -t simoc_flask_mysql_k8s .
```

### Re-build a `simoc_celery_worker_k8s` image
```bash
docker build -f celery_worker/Dockerfile -t simoc_celery_worker_k8s .
```

### Push images to the `Container Registry`
```bash
docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
```

### Re-deploy `SIMOC` backend using new images
```bash
kubectl replace --force -f k8s/deployments/simoc_flask_server.yaml
kubectl replace --force -f k8s/deployments/simoc_celery_cluster.yaml
```
