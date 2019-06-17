# Introduction
This guide describes the process of deploying `SIMOC` web application to the `Google Cloud Platform (GCP)` through the following set of steps:
1. Creating a new `GCP` project
2. Setting up the environment
3. Connecting to the `SIMOC` `GitHub` repository
4. Building a `SIMOC` docker image
5. Spinning up a `Kubernetes` cluster
6. Deploying a `SIMOC` image to the cluster
7. Accessing the `SIMOC` app

The guide covers two basic deployment scenarios:
* [Using Google Cloud Shell (Ubuntu environment)](#scenario-1)
* [Deployment from local Linux/macOS](#scenario-2)

# `GCP` Architecture Diagram
![Architecture Diagram](deployment_templates/images/GCP_architecture_diagram.png)

# Configure a `GCP` Project

### 1. Login to the `Cloud Console`
* https://cloud.google.com/

### 2. Make yourself familiar with the `Cloud Console`
* https://console.cloud.google.com/getting-started

### 3. Create or select a `GCP` project
* https://cloud.google.com/resource-manager/docs/creating-managing-projects

### 4. Make sure that billing is enabled for your project
* https://cloud.google.com/billing/docs/how-to/modify-project

### 5. Navigate to the API Library
* https://console.cloud.google.com/apis/library

### 6. Activate the following APIs
* Compute Engine API
* Kubernetes Engine API
* Google Container Registry API

# Scenario 1

## Deploy `SIMOC` (using `Cloud Shell`)

### Initialize a new `Cloud Shell` session
* https://cloud.google.com/shell/docs/quickstart
* https://console.cloud.google.com/cloudshell

### Select `GCP` Project and Zone
Check the current configuration:
```bash
gcloud config list
```
Select the `Project` and the `Compute Zone` for the deployment
```bash
gcloud projects list
gcloud compute zones list
```
```bash
export GCP_PROJECT_ID=<PROJECT_ID>
export GCP_ZONE=<GCP_ZONE>
```

Set up `Project` and `Zone` config
```bash
gcloud config set project $GCP_PROJECT_ID
gcloud config set compute/zone $GCP_ZON
```
Please note your selection as you will need those values later on in this guide.

### Install `Helm` client tool (`package manager for k8s`)
```bash
curl -LO https://git.io/get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```

### Configure `GitHub` `SSH` access

Generate a new `SSH` key (`use empty passphrase`)
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Copy the content of the `id_rsa.pub` file to your clipboard
```bash
cat ~/.ssh/id_rsa.pub
```

Use the following guide starting from the `Step 2` to add the SSH key to your GitHub account:
* https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

### Clone the `SIMOC` codebase
```bash
cd ~/
git clone -b abm_database git@github.com:kstaats/simoc.git
cd simoc/
```

### Build `SIMOC` image

Configure a `Docker` environment:
```bash
gcloud auth configure-docker
```

Build a `simoc_server_mysql` image:
```bash
docker build -t simoc_server_mysql --build-arg APP_PORT=8000 .
```

Push an image to `Container Registry`:
```bash
docker tag simoc_server_mysql gcr.io/$GCP_PROJECT_ID/simoc:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc:latest
```

### Set up a `Kubernetes` cluster

Create a `Kubernetes` cluster:
```bash
gcloud container clusters create k0 \
    --preemptible \
    --zone $GCP_ZONE \
    --machine-type=n1-standard-4 \
    --num-nodes 2 --enable-autoscaling --min-nodes 1 --max-nodes 5
```

Set up a `Kubernetes` environment:
```bash
gcloud container clusters get-credentials k0 --zone $GCP_ZONE
```


### Deploy `SIMOC` to `Kubernetes` cluster

Deploy and init a `Helm` backend to the cluster:
```bash
kubectl create -f deployment_templates/other/helm-rbac-config.yaml
helm init --service-account tiller --history-max 200 --upgrade
```

Deploy `MySQL` server to the cluster:
```bash
helm repo update
helm install --name simoc-db \
    --set mysqlDatabase=simoc \
    --set resources.requests.cpu=1.0 \
    --set resources.requests.memory=512Mi \
    --set resources.limits.cpu=1.0 \
    --set resources.limits.memory=512Mi \
    stable/mysql
```

Save the `MySQL` credentials to the `Cloud Secrets`:
```bash
export DB_TYPE=mysql
export DB_HOST="simoc-db-mysql.default.svc.cluster.local"
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=$(
    kubectl get secret --namespace default simoc-db-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode
    echo
)
kubectl create secret generic simoc-db-config \
    --from-literal=db_type=$DB_TYPE \
    --from-literal=db_host=$DB_HOST \
    --from-literal=db_port=$DB_PORT \
    --from-literal=db_name=$DB_NAME \
    --from-literal=db_user=$DB_USER \
    --from-literal=db_password=$DB_PASSWORD
```

Create static public IP address for `SIMOC`:
```bash
gcloud compute addresses create simoc-static-ip --global
```

Deploy `Nginx Ingress` service to the cluster:
```bash
helm install --name nginx-ingress stable/nginx-ingress
```

Access the `Code Editor` from the toolbar by clicking the pencil icon:
* https://cloud.google.com/shell/docs/features#code_editor

Open the `~/simoc/deployment_templates/deployments/simoc_server.yaml` file.<br><br>
Fill in the `<PROJECT_ID>` value in the `spec/spec/containers/image` section:
```bash
image: gcr.io/<PROJECT_ID>/simoc:latest
```

Deploy `SIMOC` backend into the cluster:
```bash
kubectl create -f deployment_templates/deployments/simoc_server.yaml
kubectl create -f deployment_templates/autoscalers/simoc_server.yaml
kubectl create -f deployment_templates/services/simoc_server.yaml
kubectl create -f deployment_templates/ingresses/simoc_server.yaml
```

`SSH` into a `SIMOC` container and initiate a database reset:
```bash
kubectl exec "$(kubectl get pods -l app=simoc-backend --output=jsonpath={.items..metadata.name})" \
    -- bash -c "python3 create_db.py"
```

If the following error occurs, wait for 1-2 minutes and retry:
```
error: unable to upgrade connection: container not found ("simoc-backend")
```

### Access `SIMOC` web application
In `Cloud Console`, navigate to the `Kubernetes Engine -> Services` tab.
* https://console.cloud.google.com/kubernetes/discovery

Once the cluster is up and running (may need to click a `Refresh` button), the `nginx-ingress-controller` service will list the HTTP/HTTPS Endpoints that you can use to access the app.

# Scenario 2

## Deploy `SIMOC` (from local `Linux/macOS`)

Install and initialize `Cloud SDK`:
* https://cloud.google.com/sdk/
* https://cloud.google.com/sdk/docs/quickstarts

Install additional SDK components (`k8s client`):
```bash
gcloud components install kubectl
```

Follow the `Cloud Shell` instructions starting from the [Select GCP Project and Zone](#select-gcp-project-and-zone)
* Use your favorite text editor and command line terminal to accomplish the steps (instead of Google Cloud Shell and Code Editor)
* Make sure you specify the right path to the SIMOC source folder (default is `$HOME` folder)

# Rollout Updates

### Re-deploy `SIMOC` on file changes

Remove an exiting `simoc_server_mysql` image (optional):
```bash
docker rmi simoc_server_mysql
```

Re-build a `simoc_server_mysql` image:
```bash
docker build -t simoc_server_mysql --build-arg APP_PORT=8000 .
```

Push a new image to `Container Registry`:
```bash
docker tag simoc_server_mysql gcr.io/$GCP_PROJECT_ID/simoc:latest
docker push gcr.io/$GCP_PROJECT_ID/simoc:latest
```

Re-deploy `SIMOC` backend using a new image:
```bash
kubectl replace --force -f deployment_templates/deployments/simoc_server.yaml
```

### Reset and re-deploy `MySQL` 

Delete the exiting `MySQL` server deployment and credentials:
```bash
helm del --purge simoc-db
kubectl delete secret simoc-db-config
```

Deploy a new `MySQL` server to the cluster:
```bash
helm repo update
helm install --name simoc-db \
    --set mysqlDatabase=simoc \
    --set resources.requests.cpu=1.0 \
    --set resources.requests.memory=512Mi \
    --set resources.limits.cpu=1.0 \
    --set resources.limits.memory=512Mi \
    stable/mysql
```

Save the new `MySQL` credentials to the `Cloud Secrets`:
```bash
export DB_TYPE=mysql
export DB_HOST="simoc-db-mysql.default.svc.cluster.local"
export DB_PORT=3306
export DB_NAME=simoc
export DB_USER=root
export DB_PASSWORD=$(
    kubectl get secret --namespace default simoc-db-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode
    echo
)
kubectl create secret generic simoc-db-config \
    --from-literal=db_type=$DB_TYPE \
    --from-literal=db_host=$DB_HOST \
    --from-literal=db_port=$DB_PORT \
    --from-literal=db_name=$DB_NAME \
    --from-literal=db_user=$DB_USER \
    --from-literal=db_password=$DB_PASSWORD
```

`SSH` into a `SIMOC` container and initiate a database reset:
```bash
kubectl exec "$(kubectl get pods -l app=simoc-backend --output=jsonpath={.items..metadata.name})" \
    -- bash -c "python3 create_db.py"
```
