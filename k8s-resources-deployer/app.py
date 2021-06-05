#! /usr/bin/env python3

import sys
import os
import yaml
import logging
import configparser
from kubernetes import client, config
from resources import pod, deployment, service, configmap, secret

# Setting logging configurations
log_level = logging.INFO
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=log_level)
log = logging.getLogger()

# Reading from config.ini
try:
    config_file = configparser.ConfigParser()
    config_file.read("config.ini")
    kubernetes_section = config_file["kubernetes"]
    pod_section = config_file["pod"]
    pod_resource_path = pod_section["resource_path"]
    deployment_section = config_file["deployment"]
    deployment_resource_path = deployment_section["resource_path"]
    service_section = config_file["service"]
    service_resource_path = service_section["resource_path"]
    configmap_section = config_file["configmap"]
    configmap_resource_path = configmap_section["resource_path"]
    secret_section = config_file["secret"]
    secret_resource_path = secret_section["resource_path"]

except e:
    log.error(e)

# Loading kubernetes configurations
try:
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
        namespace_path = kubernetes_section["namespace_path_inside_pod"]
        with open(namespace_path) as file:
            namespace = file.read().strip()
            file.close()
    else:
        config.load_kube_config()
        namespace = kubernetes_section["namespace"]
    v1 = client.CoreV1Api()
    appsv1 = client.AppsV1Api()
except e:
    log.error(e)
    sys.exit(-1)


def parse_yaml(path):
    try:
        with open(os.path.join(os.path.dirname(__file__), path)) as file:
            yamlbody = yaml.safe_load(file)
            file.close()
            return yamlbody
    except FileNotFoundError as error:
        log.error(error)
        log.error(error.strerror)
        sys.exit(-1)
    except yaml.parser.ParserError as error:
        log.error(error)
        sys.exit(-1)




def main():
    # Pod resources
    log.debug("Reading Pod Definition from {}".format(pod_resource_path))
    yaml_parsed = parse_yaml(pod_resource_path)
    log.debug("Resource defintion for pod: {}".format(yaml_parsed))
    pod.create_pod(api_group=v1, namespace=namespace, resource_definition=yaml_parsed, logger=log)


    # Deployment resources
    log.debug("Reading Deployment Definition from {}".format(deployment_resource_path))
    yaml_parsed = parse_yaml(deployment_resource_path)
    log.debug("Resource defintion for deployment: {}".format(yaml_parsed))
    deployment.create_deployment(api_group=appsv1, namespace="backend-team", resource_definition=yaml_parsed, logger=log)


    # Service resources
    log.debug("Reading Service Definition from {}".format(service_resource_path))
    yaml_parsed = parse_yaml(service_resource_path)
    log.debug("Resource defintion for service: {}".format(yaml_parsed))
    service.create_service(api_group=v1, namespace="backend-team", resource_definition=yaml_parsed, logger=log)


    # ConfigMap resources
    log.debug("Reading ConfigMap Definition from {}".format(configmap_resource_path))
    yaml_parsed = parse_yaml(configmap_resource_path)
    log.debug("Resource defintion for configmap: {}".format(yaml_parsed))
    configmap.create_configmap(api_group=v1, namespace="backend-team", resource_definition=yaml_parsed, logger=log)


    # Secret resources
    log.debug("Reading Secret Definition from {}".format(secret_resource_path))
    yaml_parsed = parse_yaml(secret_resource_path)
    log.debug("Resource defintion for secret: {}".format(yaml_parsed))
    secret.create_secret(api_group=v1, namespace="backend-team", resource_definition=yaml_parsed, logger=log)

if __name__ == "__main__":
    main()