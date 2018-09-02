#!/bin/bash
# Fill in the GCP project details (project, zone)
GCP_PROJECT_ID="<GCP_PROJECT_ID>"
GCP_ZONE="<GCP_ZONE>"

# Define the MySQL user password (it will be propagated to the SIMOC server through ENV variables)
MYSQL_USER="proxyuser"
MYSQL_PASSWORD="<MYSQL_PASSWORD>"
MYSQL_DB="proxyuser"

# Create a k8s cluster
gcloud container clusters create k0 \
--preemptible \
--zone $GCP_ZONE \
--machine-type=n1-standard-4 \
--num-nodes 2 --enable-autoscaling --min-nodes 1 --max-nodes 5
sleep 30

# Get cluster configuration from GCP
gcloud container clusters get-credentials k0 --zone $GCP_ZONE

# Initialize and deploy Helm
kubectl create serviceaccount --namespace kube-system tiller
kubectl create -f other/tiller-clusterrolebinding.yaml
helm init --service-account tiller --upgrade
sleep 30

# Deploy MySQL pod to the cluster
helm install --name mysqldb \
  --set mysqlUser=$MYSQL_USER \
  --set mysqlPassword=$MYSQL_PASSWORD \
  --set mysqlDatabase=$MYSQL_DB \
  stable/mysql

# Deploy Nginx Ingress pod to the cluster
helm install --name nginx-ingress stable/nginx-ingress
sleep 30

# Save MySQL creadentials to the Cloud Secrets
kubectl create secret generic simoc-db-credentials \
    --from-literal=username=$MYSQL_USER --from-literal=password=$MYSQL_PASSWORD

# Create static IP address
gcloud compute addresses create simoc-static-ip --global

# Deploy SIMOC server pods
kubectl create -f deployments/simoc_server.yaml
kubectl create -f autoscalers/simoc_server.yaml
kubectl create -f services/simoc_server.yaml
kubectl create -f ingresses/simoc_server.yaml
