import os
import yaml
import json
from kubernetes.client import exceptions


def list_pods(api_group, namespace, logger):
    pods_list = []
    pods_object = api_group.list_namespaced_pod(namespace=namespace)
    logger.info("GETTING AVAILABLE PODS FROM '{}' NAMESPACE".format(namespace.upper()))
    if (pods_object.items != []):
        for pod in pods_object.items:
            pods_list.append(pod.metadata.name)
    else:
        logger.debug("No pods available in {} namespace".format(namespace))
    return pods_list
        

def create_pod(api_group, namespace, resource_definition, logger):
    pod_metadata = resource_definition["metadata"]
    pod_name = pod_metadata["name"]

    deployed_pods = list_pods(api_group=api_group, namespace=namespace, logger=logger)
    logger.info("Deployed Pods are: {}".format(deployed_pods))

    # Verifying the namespace before deploying
    if ("namespace" in pod_metadata) and (pod_metadata["namespace"] != namespace):
        logger.warn("The pod can only be deployed to '{}' namespace, (namespace in resource definition: '{}')" \
                    "fixing the namespace in the resource definition".format(namespace, pod_metadata["namespace"]))
        resource_definition["metadata"]["namespace"] = namespace
        logger.warn("Updated Resource defintion for pod: {}".format(resource_definition))
    
    # Creating New Pod or Updating if already deployed
    if (pod_name not in deployed_pods):
        logger.info("'{}' not available pods list, deploying it".format(pod_name))
        try:
            logger.debug("Deploying '{}' pod in '{}' namespace".format(pod_name, namespace))
            response = api_group.create_namespaced_pod(body=resource_definition, namespace=namespace)
            logger.info("Pod '{}' created successfully".format(response.metadata.name))
            return("Pod '{}' created successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
    else:
        logger.info("'{}' already available in the pods list, patching it with latest resource definition".format(pod_name))
        try:
            response = api_group.patch_namespaced_pod(name=pod_name ,body=resource_definition, namespace=namespace)
            logger.info("Pod '{}' patched successfully".format(response.metadata.name))
            return("Pod '{}' patched successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
            logger.error("Pod configurations cannot be modified, please delete the pod and create again.")