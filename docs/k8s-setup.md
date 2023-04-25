---
title: Enterprise Cloud setup guide
---

This document will guide you to install Practicus AI Enterprise Cloud Kubernetes backend. 

There are multiple backend options and Kubernetes is one of them. Please [view the detailed comparison table](https://practicus.ai/cloud/#compare) to learn more. 


## Overview

Practicus AI kubernetes backend have some mandatory and optional components.

### Mandatory components

* **Kubernetes cluster**
* **Kubernetes namespace**: Usually named **prt-ns**
* **Management database**: Low traffic database that holds users, connections, and other management components. Can be inside or outside the kubernetes cluster.
* **Console Deployment**: Management console and APIs that the Practicus AI App or SDK communicates with.
* **Istio Service Mesh**: Secures, routes and load balances network traffic. You can think of it as an open source and modern NGINX Plus.   

### Optional components

* **Optional Services Deployment**: Only required if you would like to enable OpenAI GPT and similar AI services.   
* **Additional kubernetes clusters**: You can use multiple clusters in different geos to build a flexible data mesh architecture.
* **Additional namespaces**: It is common practicus practice to deploy at least one more namespace as a test environment, usually named prt-ns2.  

### Dynamic components

* **Cloud worker pods**: These are ephemeral (temporary) pods created and disposed by the management console service. E.g. When a user wants to process large data, perform AutoML etc., the management console creates worker pod(s) on the fly, and disposes after the user is done. The dynamic capacity offered to end users is highly governed by system admins.      

### Big Picture

![k8s-setup-overview](img/k8s-setup-overview.png)

## Before You start 

Please make sure you have the following:

- Practicus AI private helm repository access token.
- (Optional) Practicus AI notification email system access key. Used for "forgot my password" type emails. You can also deploy your own email system.
- (Optional) [OpenAI account and private API key](https://platform.openai.com/account/api-keys), if you would like to enable GPT.

## Prerequisites

Before installing Practicus AI admin console, please make sure you complete the below prerequisite steps. 

Installation scripts assume you use macOS, Linux or WSL on Windows.  

### Create or reuse a Kubernetes Cluster

Please create a new Kubernetes cluster if you do not already have one. For this document, we will use a new Kubernetes cluster inside Docker Desktop. Min 8GB RAM for Docker engine is recommended. Installation steps are similar for other Kubernetes environments, including cloud ones such as AWS EKS.

[View Docker Desktop memory settings](https://docs.docker.com/config/containers/resource_constraints/)

[View Docker Desktop Kubernetes setup guide](https://docs.docker.com/desktop/kubernetes/)

### Create or reuse PostgreSQL Database

Practicus AI management console uses PostgreSQL database to store some configuration info such user credentials, database connections and more.

This is a management database with low transaction requirements even for production purposes.    

```shell
echo "***"
echo "Deleting existing development database"
echo "***"

docker container stop prt-db-console
docker rm prt-db-console

echo "***"
echo "Creating new development database prt-db-console"
echo "***"

docker pull postgres:latest
docker run \
    --name prt-db-console \
    -p 5432:5432 \
    -e POSTGRES_USER=console \
    -e POSTGRES_PASSWORD=console \
    -e POSTGRES_DB=console \
    -d postgres
```

### Install kubectl 

Install kubectl CLI tool to manage Kubernetes clusters 

```shell
echo "***"
echo "Installing kubectl"
echo "***"
curl -LO "https://dl.k8s.io/release/v1.25.8/bin/darwin/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
sudo chown root: /usr/local/bin/kubectl
```

### Install Helm

Practicus AI installation is easiest using helm charts. 

```shell
echo "***"
echo "Installing Helm"
echo "***"
curl -fsSL -o get_helm.sh \
  https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
rm get_helm.sh
```

### Verify current kubectl context

Make sure kubectl is pointing to the correct Kubernetes cluster

```shell
kubectl config current-context

# Switch context to Docker Desktop if required 
kubectl config use-context docker-desktop
```

### Install Istio service mesh

Practicus AI uses Istio to ingest, route traffic, secure and manage the modern data mesh microservices architecture.

Istio can be installed on any Kubernetes cluster and designed to run side by side with any umber of other production workloads. Istio will not interfere with a namespace unless you ask Istio to do so.

[Learn more about Istio](https://istio.io/latest/about/service-mesh/) 

The below script downloads the latest istoctl version, e.g. 1.17.2. 

Please update the "mv istio-1.17.2 istio" section below to a newer version if required.   

```shell
cd ~ || exit
echo "***"
echo "Downloading Istio"
echo "***"
rm -rf istio
curl -L https://istio.io/downloadIstio | sh -
mv istio-1.17.2 istio || \
  echo "*** Istio version is wrong in this script. \
        Please update to the version you just downloaded to your home dir ***"
cd ~/istio || exit
export PATH=$PWD/bin:$PATH

echo "***"
echo "Analyzing Kubernetes for Istio compatibility"
echo "***"
istioctl x precheck 

echo "***"
echo "Installing Istio"
echo "***"
istioctl install --set profile=default -y

echo "***"
echo "Recommended: Add istioctl to path"
echo "***"
# Add the below line to .zshrc or alike
# export PATH=~/istio/bin:$PATH
```

### (Recommended) Install Practicus AI app and configure local docker

This step is mandatory if you do not have your Enterprise license key. 

By installing Practicus AI app you will be able to test connectivity to your newly created Kubernetes cluster. You will also have access to your Enterprise license key.
 
* [Install the app](https://practicus.ai/get-started/)
* Go to settings > container section
* Enter your email to activate your enterprise license 
* [View Practicus AI local docker setup guide](trial-ent.md) if you need any help

Once your enterprise license is activated, please open ~/.practicus/core.conf file on your computer, locate the **license** section, and copy **license_key** info.

Sample license_key inside ~/.practicus/core.conf : 
```
[license]
email = your_email@your_company.com
license_key = abc12345-1234-1234-12ab-123456789012
valid_until = Wed, 01 Jan 2022 00:00:00 GMT
```

## Preparing a Kubernetes namespace

Practicus AI Kubernetes backend is designed to run in a namespace and side-by-sde with other production workloads. 

We strongly suggest you use namespaces, even for testing purposes.

### Create namespace

You can use multiple namespaces for Practicus AI ,and we will use the name convention: prt-ns (e.g. for production), prt-ns2 (for testing) etc.

In this document we will only use one namespace, prt-ns.  

```shell
echo "***"
echo "Creating namespace prt-ns"
echo "***"
kubectl create namespace prt-ns
```

### Enable Istio for selected Kubernetes namespace(s)

Enabling Istio will inject a sidecar to all Kubernetes pods for the **selected namespace** only.

```shell
echo "***"
echo "Enabling Istio for namespace prt-ns"
echo "***"
kubectl label namespace prt-ns istio-injection=enabled

echo "***"
echo "Analyzing Istio setup for namespace prt-ns"
echo "***"
istioctl analyze -n prt-ns
```

## Add practicusai helm repository

Practicus AI helm repository is a private repository that makes installing Practicus AI console backend easier.

Please make sure you have a GitHub personal access token which has not expired, and replace the below script with it. 

```shell
eco "Setting private helm repo token"
PRT_HELM_TOKEN=github_pat_xyz

echo "Adding private practicusai helm repo"
helm repo add practicusai \
  --username "$PRT_HELM_TOKEN" \
  --password "$PRT_HELM_TOKEN" \
  "https://raw.githubusercontent.com/practicusai/helm/master/"
  
echo "Private helm repo access tokens expire regularly. \
      Please request request a new token if access is denied"
  
echo "Updating all helm repos on your computer"
helm repo update

echo "Viewing charts in practicusai repo"
helm search repo practicusai

```

## Deploying Management Console 

### Helm chart values.yaml

Practicus AI helm chart's come with many default values that you can leave as-is, especially for local dev/test configurations. 

For all other settings, we suggest you to use values-x.yaml files

```shell
mkdir ~/practicus 
mkdir ~/practicus/helm
cd ~/practicus/helm
touch values-console-local.yaml
touch values-console-prod.yaml
```

Sample **values-console-local.yaml** file contents for a **local test environment**

```shell
cat <<EOF >>values-console-local.yaml

migrate:
  superUserEmail: "your_email@your_company.com"
  superUserPassword: "first super admin password"

enterpriseLicense:
  email: "your_email@your_company.com"
  key: "__add_your_key_here__"
  
database:
  engine: POSTGRESQL
  host: host.docker.internal
  name: console
  user: console
  password: console

advanced:
  debugMode: true
  logLevel: DEBUG

notification:
  api_auth_token: "(optional) _your_email_notification_api_key_"
  
EOF
```

Sample **values-console-prod.yaml** file contents for a **production environment**

```shell
cat <<EOF >>values-console-prod.yaml

main:
  # Dns accessible by app
  host: practicus.your_company.com
  ssl: true

migrate:
  superUserEmail: "your_email@your_company.com"
  superUserPassword: "first super admin password"

enterpriseLicense:
  email: "your_email@your_company.com"
  key: "__add_your_key_here__"

database:
  engine: POSTGRESQL
  host: "ip address or dns of db"
  name: "db_name"
  user: "db_user"
  password: "db_password"

jwt:
  # API JWT token issuer, can be any value 
  issuer: iss.my_company.com

notification:
  api_auth_token: "(optional) _your_email_notification_api_key_"
  
EOF
```

### Ingress for AWS EKS

This step is not required for a local test setup. 

For AWS, our helm charts automatically configure Application Load Balancer and SSL certificates. 

You can simply add the below to values-console-prod.yaml file.

```yaml
aws:
  albIngress: true
  # AWS Certificate Manager (ACM) certificate ARN for your desired host address
  certificateArn: _add_your_ACM_cert_ARN_here_
  # sharedAlb = true is required only if you need to share ALBs between gateways to save on ALB cost.
  sharedAlb: false
```

### Ingress and other settings for various Kubernetes systems

Please check the below documentation to configure Istio and Istio gateway depending on your Kubernetes infrastructure. 

* [Azure](https://istio.io/latest/docs/setup/platform-setup/azure/)
* [Google Cloud](https://istio.io/latest/docs/setup/platform-setup/gke/)
* [OpenShift](https://istio.io/latest/docs/setup/platform-setup/openshift/)
* [Oracle Cloud](https://istio.io/latest/docs/setup/platform-setup/oci/)
* [IBM Cloud](https://istio.io/latest/docs/setup/platform-setup/ibm/)
* [MicroK8s](https://istio.io/latest/docs/setup/platform-setup/microk8s/)

### Configuring management database

Since the management console will immediately try to connect to its database, it makes sense to prepare the database first. 

The below steps will create a temporary pod that will create or update the necessary tables and populate initial data.

```shell
cd ~/practicus/helm

# Confirm you are using the correct kubernetes environment
kubectl config current-context

# Replace the below values-x.yaml file with dev/test/prod configurations
  
# Step 1) Create a temporary pod that will create (or update) the database

helm install prt-migrate-console-db practicusai/practicus-migrate-console-db \
  --namespace prt-ns \
  --set advanced.imagePullPolicy=Always \
  --values ./values-console-local.yaml

# Step 2) View the db migration pod status and logs. 
#   Run it multiple times if pulling the container takes some time.  

echo "DB migration pod status"
echo "-----------------------"
kubectl get pod -n prt-ns | grep prt-pod-migrate-db
echo ""
echo "Pod logs"
echo "--------"
kubectl logs --follow prt-pod-migrate-db -n prt-ns
```

Once the database migration is completed, you will see success log messages such as the below: 

```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0001_initial... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
...
```

```shell
# Step 3) (Recommended) After you confirm that the tables are created,
#   you can safely terminate the database migration pod using helm.
#   If you do not, the pod will self-terminate after 10 minutes. 

helm uninstall prt-migrate-console-db --namespace prt-ns 
```

You can repeat the above 1-3 steps as many times as you need, and for each new version of the management console. 

If there are no updates to the database schema, the pod will not make any changes.   

### Installing management console

```shell
cd ~/practicus/helm
helm repo update 

# Replace the below values-x.yaml file with dev/test/prod configurations

helm install practicus-console practicusai/practicus-console \
  --namespace prt-ns \
  --values values-console-local.yaml
```

### Logging in to management console

You should be able to log in to Practicus AI management console using [http://127.0.0.1/console/admin](http://127.0.0.1/console/admin) or https://practicus.your_company.com/console/admin

Your super admin username / password is at the top of your values-x.yaml file. 

### Troubleshooting

```shell
# Find the pod name(s)
kubectl -n prt-ns get pod | grep prt-depl-console-

# View status
kubectl -n prt-ns describe pod prt-depl-console-...

# View logs
kubectl -n prt-ns logs --follow prt-depl-console-...

# Analyze using the interactive terminal
kubectl -n prt-ns exec -it prt-depl-console-... -- /bin/bash  
```

### Upgrading management console to a newer version

```shell
cd ~/practicus/helm
helm repo update

# Replace the below values-x.yaml file with dev/test/prod configurations

helm upgrade practicus-console practicusai/practicus-console \
  --namespace prt-ns \
  --values values-console-local.yaml
```

### Uninstalling management console 

```shell
helm uninstall practicus-console --namespace=prt-ns
```

### (Recommended) Start a new Cloud Worker using Practicus AI App

* Open Practicus AI App
* Go to settings > click login
* Enter service address e.g. http://127.0.0.1 or https://practicus.your_company.com
* You can use your super admin user / password
* Click on either Explore or Cloud at the top bar
* For Explore: You should see a new "Practicus AI Service" (can be renamed later)
* Click on "New Worker", select a size (if on your laptop, select 1 or 2 GB RAM)
* For Cloud: Select the newly added region (upper right)
* Click "Start New", select a size (if on your laptop, select 1 or 2 GB RAM)

This will start pulling the Cloud Worker image on first use, which can take a while. During this time the app will show the Cloud Worker (pod) status as pending. Once the pull is completed the app will notify you. Go to Explore tab, click on "Worker-x Files" (x is the counter) and view the local disk content of the pod. This verifies everything is deployed correctly. 

### Troubleshooting Cloud Workers 

```shell
# Find the pod name(s)
kubectl -n prt-ns get pod | grep prt-pod-wn-

# View status
kubectl -n prt-ns describe pod prt-pod-wn-...

# View logs
kubectl -n prt-ns logs --follow prt-pod-wn-...

# Analyze using the interactive terminal
kubectl -n prt-ns exec -it prt-pod-wn-... -- /bin/bash  
```

### (Recommended) Installing Practicus AI services (GPT etc.)

Practicus AI services can use the same values-x.yaml file as the management console deployment.

If you obtained an OpenAI API key, please follow the below steps to enable GPT.    


### Installing optional services

```shell
cd ~/practicus/helm
helm repo update 

# Replace the below values-x.yaml file with dev/test/prod configurations

helm install practicus-services practicusai/practicus-services \
  --namespace prt-ns \
  --values values-console-local.yaml
```

### Troubleshooting optional services deployment

```shell
# Find the pod name(s)
kubectl -n prt-ns get pod | grep prt-depl-services-

# View status
kubectl -n prt-ns describe pod prt-depl-services-...

# View logs
kubectl -n prt-ns logs --follow prt-depl-services-...

# Analyze using the interactive terminal
kubectl -n prt-ns exec -it prt-depl-services-... -- /bin/bash
```  

### Upgrading optional services deployment to a newer version

```shell
cd ~/practicus/helm
helm repo update

# Replace the below values-x.yaml file with dev/test/prod configurations

helm upgrade practicus-services practicusai/practicus-services \
  --namespace prt-ns \
  --values values-console-local.yaml
```

### Uninstalling optional services deployment

```shell
helm uninstall practicus-services --namespace=prt-ns
```

### Optional services additional settings 

Some optional services such as OpenAI GPT require additional setup.

Sample setup:

* Open management console e.g. http://127.0.0.1/console/admin
* Go to "Machine Learning Services" > "API Configurations" page
* Click "Add API Configuration"
* Select OpenAI GPT
* Enter your API key that you obtained from OpenAI E.g. "sk-abc123..." [View your key](https://platform.openai.com/account/)
* In optional settings section add the below 

```
OpenAI-Organization=org-your_org_id_on_open_AI
model=gpt-4
max_tokens=350
```

* **OpenAI-Organization** You can find this id on [OpanAI account page]((https://platform.openai.com/account/)) 
* **model** You can choose between gpt-3.5-turbo, gpt-4 etc. [View available models](https://platform.openai.com/docs/models/overview) 
* **max_tokens** This is a cost control measure preventing high OpenAI costs. The system logs tokens used by your users, so you can adjust this number later.

### Management console settings

There are several settings on the management console that you cna easily change using the admin console page.

These changes are stored in the management database, so we strongly suggest you to regularly back up your database.

* Groups: We strongly suggest you to create groups before granting right.s e.g. power users, data scientists .. 
* Users: You can create users and give fine-grained access to admin console elements.
* Staff users can log in to admin console. Most users should not and only use Practicus AI App
* **Central Configuration** Please visit "Cluster Definitions" to change your service name and location ASAP. E.g. "Practicus AI Service" "Seattle". When end users login through the App, this is the information they will see and this is cached for future use.    
* **Cloud Worker Admin** It is crucial you visit every page on this section and adjust Cloud Worker (pod) capacity settings. 
* **Connection Admin** Users can only use analytical database connections that they add to the system AND the connections you make visible to certain groups / users. 
* **SaaS Admin** This section is only used if you activate self-service SaaS through a 3rd party payment gateway. We suggest only the super admin has access to it, and you make this section invisible to all other admin or staff users.


### Advanced settings

Practicus AI helm charts values.yaml files include many advanced settings and explanations as inline comments. Please navigate and alter these settings, upgrade your deployments and validate the state as you see fit.

Please see below a sample values.yaml file where you can adjust replica count etc.: 
```yaml
...
capacity:
  # Console API service replica
  replicas: 1

  # Cloud Worker ephemeral disk capacity proportional to RAM.
  # E.g.: 0.5 means 500MB ephemeral disk for each 1GB Ram
  diskToRamRatio: 1

  # Max workers per Cloud Worker.
  # Every time a user opens a worksheet on the app a worker process is created inside the Cloud Worker
  maxWorkerToRamRatio: 10
...
```

## Support 

Need help? Please visit [https://practicus.ai/support/](https://practicus.ai/support/) to open a support ticket.

Thank you!
