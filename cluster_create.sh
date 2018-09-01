#!/bin/bash
GCP_PROJECT_ID="<GCP_PROJECT_ID>"
GCP_ZONE="<GCP_ZONE>"

MYSQL_USER="proxyuser"
MYSQL_PASSWORD="<MYSQL_PASSWORD>"
MYSQL_DB="proxyuser"

gcloud container clusters create k0 \
--zone $GCP_ZONE \
--machine-type=n1-standard-4 \
--num-nodes 2 --enable-autoscaling --min-nodes 1 --max-nodes 5
sleep 30

gcloud container clusters get-credentials k0

kubectl create serviceaccount --namespace kube-system tiller
kubectl create -f other/tiller-clusterrolebinding.yaml
helm init --service-account tiller --upgrade
sleep 30

helm install --name mysqldb \
  --set mysqlUser=$MYSQL_USER \
  --set mysqlPassword=$MYSQL_PASSWORD \
  --set mysqlDatabase=$MYSQL_DB \
  stable/mysql

helm install --name nginx-ingress stable/nginx-ingress
sleep 30

kubectl create secret generic simoc-db-credentials \
    --from-literal=username=$MYSQL_USER --from-literal=password=$MYSQL_PASSWORD

gcloud compute addresses create simoc-static-ip --global

gsutil iam ch allUsers:objectViewer gs://artifacts.$GCP_PROJECT_ID.appspot.com

kubectl create -f deployments/simoc_server_v2.yaml
kubectl create -f autoscalers/simoc_server.yaml
kubectl create -f services/simoc_server.yaml
kubectl create -f ingresses/simoc_server.yaml
