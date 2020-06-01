# Deploy `SIMOC` to `Google Kubernetes Engine (GKE)`

# 1. Configure `GCP` Project

## Login to the `Cloud Console`
* https://cloud.google.com/

## Create or select a `GCP` project
* https://cloud.google.com/resource-manager/docs/creating-managing-projects

## Make sure that billing is enabled for your project
* https://cloud.google.com/billing/docs/how-to/modify-project

## Navigate to the API Library
* https://console.cloud.google.com/apis/library

## Activate the following APIs
* Compute Engine API
* Kubernetes Engine API
* Google Container Registry API

## Initialize a new `Cloud Shell` session
* https://console.cloud.google.com/getting-started
* https://cloud.google.com/shell/docs/quickstart
* https://console.cloud.google.com/cloudshell

# 2. Configure `SIMOC` deployment

#### Make sure you logged in and retrieved the `GCP` credentials
```bash
gcloud auth login
gcloud auth application-default login
```

#### Configure `SSH` access for `GitHub`
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

#### Clone `SIMOC` code from `GitHub`
```bash
cd ~/
git clone git@github.com:kstaats/simoc.git
cd simoc/
```

#### Open the `simoc_k8s.env` file with any text editor
```bash
vim simoc_k8s.env
```

#### Update the deployment configuration with the following variables
- `GCP_PROJECT_ID` - string ID of the GCP project (execute `gcloud projects list` to get all available options)
- `GCP_ZONE` - GCP regional zone to deploy all SIMOC resources (execute `gcloud compute zones list` to get all available options)
- `K8S_CLUSTER_NAME` - string name for the Kubernetes cluster
- `K8S_MIN_NODES` - minimum number of nodes in the cluster
- `K8S_MAX_NODES` - maximum number of nodes in the cluster (auto-scaling)
- `MIN_FLASK_REPLICAS` - minimum number of Flask worker containers
- `MAX_FLASK_REPLICAS` - maximum number of Flask worker containers (auto-scaling)
- `MIN_CELERY_REPLICAS` - minimum number of Celery worker containers
- `MAX_CELERY_REPLICAS` - maximum number of Celery worker containers (auto-scaling)
- `SERVER_NAME` - DNS hostname for the SIMOC application
- `ACME_EMAIL` - email address for the SSL certificate from LetsEncrypt 
- `ACME_STAGING` - `1` to use testing LetsEncrypt servers, `0` to use production servers instead (default: `1`)
- `BASIC_AUTH` - `1` to use Basic HTTP Authentication (default: `0`)
- `AUTH_USERNAME` - username for Basic Auth
- `AUTH_PASSWORD` - password for Basic Auth
- `STATIC_IP_NAME` - string name for a static external IP address
```bash
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
```

#### Load `SIMOC` configuration into the environment
```bash
source simoc_k8s.env
```

#### Set up `GCP Project` and `Zone`
```bash
gcloud config set project $GCP_PROJECT_ID
gcloud config set compute/zone $GCP_ZONE
```

#### Install `Helm` client (`package manager for k8s`)
```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```

#### Register `Helm` repositories
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://kubernetes-charts.storage.googleapis.com/
helm repo add traefik https://containous.github.io/traefik-helm-chart
helm repo update
```

# 3. Build `SIMOC` images

#### Configure `Docker` environment
```bash
gcloud auth configure-docker
```

#### Build `Docker` images
```bash
docker build -t simoc_flask_mysql_k8s .
docker build -f celery_worker/Dockerfile -t simoc_celery_worker_k8s .
```

#### Push images to `Container Registry`
```bash
docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
```

# 4. Create `Kubernetes` cluster
```bash
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
```

# 5. Deploy `SIMOC` to the cluster

#### Configure `Kubernetes` client (`kubctl`)
```bash
gcloud container clusters get-credentials $K8S_CLUSTER_NAME --zone $GCP_ZONE
```

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

#### Save `MySQL` credentials to `Cloud Secrets`
```bash
export DB_PASSWORD=$(
    kubectl get secret --namespace default simoc-db-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode
    echo
)
kubectl create secret generic simoc-db-creds --from-literal=db_password=$DB_PASSWORD
```

#### Deploy `Redis` server
```bash
curl -Lo values-production.yaml https://raw.githubusercontent.com/bitnami/charts/master/bitnami/redis/values-production.yaml
helm install redis bitnami/redis --values values-production.yaml
```

#### Save `Redis` credentials to `Cloud Secrets`
```bash
export REDIS_PASSWORD=$(
    kubectl get secret --namespace default redis -o jsonpath="{.data.redis-password}" | base64 --decode
    echo
)
kubectl create secret generic redis-creds --from-literal=redis_password=$REDIS_PASSWORD
```

#### Configure and save `Flask` secret string to `Cloud Secrets`
```bash
export FLASK_SECRET='ENTER_RANDOM_STRING_VALUE'
kubectl create secret generic flask-secret --from-literal=flask_secret=$FLASK_SECRET
```

#### Create a static IP address for `SIMOC` application
```bash
gcloud compute addresses create $STATIC_IP_NAME --region $GCP_REGION
```

#### Generate `Kubernetes` manifests
```bash
python3 generate_k8s_configs.py
```

#### Deploy `SIMOC` backend into the cluster
```bash
kubectl create -f k8s/deployments/redis_environment.yaml
kubectl create -f k8s/deployments/simoc_db_environment.yaml
kubectl create -f k8s/deployments/simoc_flask_server.yaml
kubectl create -f k8s/deployments/simoc_celery_cluster.yaml
kubectl create -f k8s/autoscalers/simoc_flask_autoscaler.yaml
kubectl create -f k8s/autoscalers/simoc_celery_autoscaler.yaml
kubectl create -f k8s/services/simoc_flask_service.yaml
```

#### Deploy `Traefik` router
```bash
helm install traefik --values k8s/ingresses/traefik_values.yaml traefik/traefik
kubectl create --force -f k8s/ingresses/traefik.yaml
kubectl patch deployment/traefik -p '{"spec": {"template": {"spec": {"initContainers": [{"name": "fix-acme", "image": "alpine:3.6", "command": ["chmod", "600", "/data/acme.json"], "volumeMounts": [{"name": "data", "mountPath": "/data"}]}]}}}}'
```

#### Initialize `MySQL` database
Execute a remote command on `simoc-flask-server` container to initiate a database reset:
```bash
kubectl exec \
    "$(kubectl get pods -l app=simoc-flask-server --output=jsonpath={.items..metadata.name} | cut -d  ' ' -f 1)" \
    -- bash -c "python3 create_db.py"
```

# 6. Roll-out updates

#### Make sure you logged in and retrieved the `GCP` credentials
```bash
gcloud auth login
gcloud auth application-default login
```

#### Load `SIMOC` configuration into the environment
```bash
source simoc_k8s.env
```

#### Set up `GCP Project` and `Zone`
```bash
gcloud config set project $GCP_PROJECT_ID
gcloud config set compute/zone $GCP_ZONE
```

#### Configure `Kubernetes` client (`kubctl`)
```bash
gcloud container clusters get-credentials $K8S_CLUSTER_NAME --zone $GCP_ZONE
```

#### Configure `Docker` environment
```bash
gcloud auth configure-docker
```

#### Re-build `simoc_flask_mysql_k8s` image
```bash
docker build -t simoc_flask_mysql_k8s .
```

#### Re-build `simoc_celery_worker_k8s` image
```bash
docker build -f celery_worker/Dockerfile -t simoc_celery_worker_k8s .
```

#### Push new images to `Container Registry`
```bash
docker tag simoc_flask_mysql_k8s gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker tag simoc_celery_worker_k8s gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_flask:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc_celery:latest
```

#### Re-deploy `SIMOC` containers with new images
```bash
kubectl replace --force -f k8s/deployments/simoc_flask_server.yaml
kubectl replace --force -f k8s/deployments/simoc_celery_cluster.yaml
```

# 7. Useful commands

#### Scale `SIMOC` components
Scale the number of `Celery` containers to `20`:
```bash
kubectl scale --replicas=20 -f k8s/deployments/simoc_celery_cluster.yaml
```

Scale the number of `Flask` containers to `5`:
```bash
kubectl scale --replicas=5 -f k8s/deployments/simoc_flask_server.yaml
```

#### Stream logs from the `flask-server` service
```bash
kubectl logs -f -l app=simoc-flask-server --all-containers --max-log-requests 100
```

#### Stream logs from the `celery-cluster` service
```bash
kubectl logs -f -l app=simoc-celery-cluster --all-containers --max-log-requests 100
```
