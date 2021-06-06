# k8s-resources-deployer
A flask based tool for creating basic kubernetes resources i.e:

- Pods
- Deployments
- Services
- Config Maps
- Secrets.

## Introduction

This tool is developed to assist developers in deploying kubernetes resources quickly and also restrict their access to the kubernetes cluster to their assigned namespace. The following assumptions have been made while deploying this tool:

- The teams are assigned a specific `namespace` in the kubernetes cluster and they will only deploy the resources to their assigned namespace.
- The `k8s-resources-deployer` runs in the same namespace the team is assigned, and the restriction of not accessing other namespaces is made sure through kubernetes RBAC policies.
- The teams will be able to access the k8s-resources-deployer through dns hostname, which is in-turn managed through ingress resource. The `nginx-ingress` is used for the current version.
- The teams will deploy resources through k8s-resources-deployer by providing yaml based manifests definitions.


## Pre-requisites

The pre-requisite for this tool is access to a kubernetes cluster with permissions of creating/updating the following resources:

- Namespaces
- Service Accounts
- Roles and Role Bindings
- Cluster Roles and Cluster Role Bindings
- Pods
- Deployments
- Services
- Ingresses

The quick way to test this tool out is through `minikube`, which is used to deploy a kubernetes cluster on a local machine. Minikube is widely used for development purposes and provides all the permissions required to run k8s-resources-deployer.

`NOTE: Minikube is not advised to be used as a production instance of kubernetes cluster and this document also advise against it.`


### Minikube Installation

This section quickly describes on getting the kubernetes cluster ready through minikube, which will be used at later stages. The Operating System used for this installation is `Ubuntu 20.04 LTS`, however the installation is done through minikube binary to make it as uniform as possible. The steps for installation are as follows:

- Download the minikube binary and install it using the following commands:
  ```bash
  $ curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  $ sudo install minikube-linux-amd64 /usr/local/bin/minikube
  ```

- Verify the installation of minikube with `minikube version` and the output would be similiar to the following:
  ```bash
  $ minikube version
  minikube version: v1.16.0
  commit: 9f1e482427589ff8451c4723b6ba53bb9742fbb1
  ```

- Create the minikube cluster with `minikube start` command. The default cluster will be created with 2 vCPUs, 2GB Memory and 20GB Hard Disk with kvm2 driver for Linux. The cluster for this document is created through docker driver using the following command:
  ```bash
  minikube start --driver=docker
  ```

- Install the kubectl utility to interact with the kubernetes cluster created in the previous step through `sudo snap --classic install kubectl` in Ubuntu. Verify the installation through `kubectl version` and the output will be similar to the one provided below:
  ```bash
  $ kubectl version
  Client Version: version.Info{Major:"1", Minor:"21", GitVersion:"v1.21.1", GitCommit:"5e58841cce77d4bc13713ad2b91fa0d961e69192", GitTreeState:"clean", BuildDate:"2021-05-13T02:40:46Z", GoVersion:"go1.16.3", Compiler:"gc", Platform:"linux/amd64"}
  Server Version: version.Info{Major:"1", Minor:"20", GitVersion:"v1.20.0", GitCommit:"af46c47ce925f4c4ad5cc8d1fca46c7b77d13b38", GitTreeState:"clean", BuildDate:"2020-12-08T17:51:19Z", GoVersion:"go1.15.5", Compiler:"gc", Platform:"linux/amd64"}
  ```

- Enable the ingress add-on in the minikube to install NGINX based ingress using `minikube addons enable ingress` command. The NGINX ingress will be used in the future stages for communicating with k8s-resources-deployer. Verify the installation with `kubectl get pods -n kube-system` and verify if the `ingress-nginx-controller-xxxxxxxxxx-xxxxx` is in running state. The output will look similar to the provided below:

  ```bash
  $ kubectl get pods -n kube-system
  NAME                                        READY   STATUS      RESTARTS   AGE
  coredns-74ff55c5b-hzhkt                     1/1     Running     1          5d4h
  etcd-minikube                               1/1     Running     1          5d4h
  ingress-nginx-admission-create-tkn5s        0/1     Completed   0          157m
  ingress-nginx-admission-patch-kwcgz         0/1     Completed   0          157m
  ingress-nginx-controller-558664778f-2fzss   1/1     Running     0          157m
  kube-apiserver-minikube                     1/1     Running     1          5d4h
  kube-controller-manager-minikube            1/1     Running     1          5d4h
  kube-proxy-bqvj8                            1/1     Running     1          5d4h
  kube-scheduler-minikube                     1/1     Running     1          5d4h
  storage-provisioner                         1/1     Running     2          5d4h2
  ```

The minikube cluster installation and configuration is complete and is ready for k8s-resources-deployer installation.


---


## Installation
The resources required to install k8s-resources-deployer are in deployment directory and can be deployed easily with the following command:

```bash
$ kubectl apply -f deployment/
clusterrole.rbac.authorization.k8s.io/k8s-deployer unchanged
deployment.apps/k8s-resource-deployer unchanged
deployment.apps/k8s-resource-deployer unchanged
ingress.networking.k8s.io/k8s-resource-deployer-ingress unchanged
ingress.networking.k8s.io/k8s-resource-deployer-ingress unchanged
service/k8s-resource-deployer unchanged
service/k8s-resource-deployer unchanged
namespace/backend-team unchanged
serviceaccount/k8s-deployer unchanged
rolebinding.rbac.authorization.k8s.io/k8s-deployer configured
namespace/frontend-team unchanged
serviceaccount/k8s-deployer unchanged
rolebinding.rbac.authorization.k8s.io/k8s-deployer configured
```

The following resources are created with the above commands:
- Cluster Role `k8s-deployer` at cluster level.
- Namespaces `backend-team` and `frontend-team`.
- Service Accounts named `k8s-deployer` in both backend-team and frontend-team namespaces.
- Role Bindings named `k8s-deployer` in both backend-team and frontend-team namespaces.
  - These Role Bindings attach Cluster Role k8s-deployer with the Service Accounts k8s-deployer to restrict the access within their respective namepsaces.
- Deployments named `k8s-resource-deployer` in both backend-team and frontend-team namespaces.
  - The pod templates has been configured to use Service Accounts k8s-deployer, so the access is limited to their respective namespace for deploying the kubernetes resources.
- Services named `k8s-resource-deployer` in both backend-team and frontend-team namespaces.
  - The service has port type set to `ClusterIP` because the access to those services will be handled by ingress configurations as described in the next step.
- Ingresses named `k8s-resource-deployer-ingress` in both backend-team and frontend-team namespaces.
  - The backend-team service will be accessible through `k8s-resource-deployer.backend.local` domain.
  - The frontend-team service will be accessible through `k8s-resource-deployer.frontend.local` domain.

The domains configured above are required to be configured in `/etc/hosts` file as the DNS is not configured at this stage. The endpoint to hit for the DNS domains will be minkube ip and following are the steps to accomplshed this:
```bash
$ sudo -i
# export MINIKUBE_IP=$(minikube ip)
# echo "$MINIKUBE_IP k8s-resource-deployer.frontend.local" >> /etc/hosts
# echo "$MINIKUBE_IP k8s-resource-deployer.backend.local" >> /etc/hosts
```

The k8s-resources-deployer is deployed in 2 separate namespaces and accessible through the domains configured above.


---
## Future Enhancements:
### Security
- Decouple the k8s-resources-deployer instance from the namespace in which workloads lies, so the resource presence in the cluster is abstracted away(Minor Release).
- Adding authentication to allow only authenticated users to access respective k8s-resources-deloyer instance (Major Release).
### Features
- Better response handling for web form after submitting the yaml resource definition (Minor Release).
- Support for more kubernetes resources (Incremental updates as Minor Releases).
- Developers use web based form to deploy resources instead of providing the yaml based manifests, which are error-prone (Major Release).