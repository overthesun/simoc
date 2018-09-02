### Login to the GCP Console
* https://cloud.google.com/

### Make yourself familiar with the GCP Console
* https://console.cloud.google.com/getting-started

### Create a GCP project
* https://cloud.google.com/resource-manager/docs/creating-managing-projects

### Navigate to the API Library
* https://console.cloud.google.com/apis/library

### Activate the following APIs
* Compute Engine API
* Kubernetes Engine API
* Google Cloud Storage
* Cloud Source Repositories API
* Google Container Registry API
* Cloud Build API
* Cloud Key Management Service API

### Deploy SIMOC (using Google Cloud Shell)

#### Initialize a new Cloud Shell session
* https://cloud.google.com/shell/docs/quickstart
* https://console.cloud.google.com/cloudshell

#### Install Helm client tool (package manager for k8s)
```bash
curl -o get_helm.sh https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get
chmod +x get_helm.sh
./get_helm.sh
```

#### Configure GitHub SSH access
Cloud Build uses personal ssh key to pull the code out of private Github repositories. Your Github account should have access to the private SIMOC repository and your Cloud Shell ssh key should be added to your Github account.

##### Generate a new SSH key (use empty passphrase)
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

##### Copy the content of the `id_rsa.pub` file to your clipboard
```bash
cat ~/.ssh/id_rsa.pub
```

##### Use the following guide starting from the `Step 2` to add the key to your GitHub account
* https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

#### Clone the SIMOC codebase
```bash
git clone -b gcp-deployment git@github.com:kstaats/simoc.git && cd simoc
```

#### Build SIMOC Image

##### Navigate to the Cloud Build templates folder
```bash
cd cloudbuild
```

##### Initialize the Key Management Service:
```bash
gcloud kms keyrings create simoc-keyring --location=global
gcloud kms keys create simoc-github-key \
--location=global --keyring=simoc-keyring \
--purpose=encryption
```

##### Encrypt your ssh key using KMS
```bash
cp ~/.ssh/id_rsa ./
chmod 777 id_rsa
gcloud kms encrypt --plaintext-file=id_rsa \
--ciphertext-file=id_rsa.enc \
--location=global --keyring=simoc-keyring --key=simoc-github-key
```

##### Copy Cloud Build service account name
Visit the GCP Console IAM menu and copy the Cloud Build service account email address, which contains `cloudbuild.gserviceaccount.com`:
* https://console.cloud.google.com/iam-admin/iam

##### Add Cloud Build `dcrypter` rights
Substitute `<SERVICE_ACCOUNT_NAME>` with the account name from the previous step):
```bash
gcloud kms keys add-iam-policy-binding \
    simoc-github-key --location=global --keyring=simoc-keyring \
    --member=serviceAccount:<SERVICE_ACCOUNT_NAME>@cloudbuild.gserviceaccount.com \
    --role=roles/cloudkms.cryptoKeyEncrypterDecrypter
```

##### Create `known_hosts` file
```bash
ssh-keyscan -t rsa github.com > known_hosts
```

##### Submit Cloud Build job (builds SIMOC image)
```bash
gcloud builds submit --config=build_simoc_image_from_github.yaml
cd ../
```

##### Grand all project users access to the Container Registry
```bash
gsutil iam ch allUsers:objectViewer gs://artifacts.<PROJECT_ID>.appspot.com
```

#### Deploy Kubernetes Cluster

##### Open Cloud Shell Code Editor
* https://console.cloud.google.com/cloudshell/editor

##### Open the `~/simoc/cluster_create.sh` file

##### Fill in the values for the empty variables and save the file
Check `gcloud config list` for the details; use secure MySQL password
```bash
gcp_project_id="<gcp_project_id>"
gcp_zone="<gcp_zone>"
mysql_password="<mysql_password>"
```

##### Open the `~/simoc/deployments/simoc_server.yaml` file

##### Fill in the `<PROJECT_ID>` value in the `spec/template/spec/containers/image` section
```bash
image: gcr.io/<PROJECT_ID>/simoc:latest
```

##### Switch back to the Cloud Shell
Run the script to spin up the cluster with the SIMOC image deployed (may take about 5-10 mins to finish):
```bash
sh cluster_create.sh
```

#### Access the SIMOC App
Navigate to the Kubernetes Services. Once the cluster is up and running (may need to click Refresh button a couple times), the `nginx-ingress-controller` service will list the HTTP/HTTPS Endpoints that you can use to access the app:
* https://console.cloud.google.com/kubernetes/discovery

### Deploy SIMOC (from local Linux/macOS)

#### Install and initialize Cloud SDK
* https://cloud.google.com/sdk/
* https://cloud.google.com/sdk/docs/quickstarts

#### Install additional SDK components (k8s client)
```bash
gcloud components install kubectl
```

#### Install Helm client (package manager for k8s)
* https://docs.helm.sh/using_helm/#installing-the-helm-client

#### Configure GitHub SSH access
Cloud Build uses personal ssh key to pull the code out of private Github repositories. Your Github account should have access to the private SIMOC repository and your ssh key should be added to your Github account. Use the following guide to make sure you have everything configured:
* https://help.github.com/articles/checking-for-existing-ssh-keys/
* https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/
* https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/

#### Follow the Cloud Shell instructions starting from the [Clone the SIMOC codebase](#Clone-the-SIMOC-codebase) section
