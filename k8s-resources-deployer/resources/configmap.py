import os
import yaml
import json
from kubernetes.client import exceptions


def list_configmaps(api_group, namespace, logger):
    configmaps_list = []
    configmaps_object = api_group.list_namespaced_config_map(namespace=namespace)
    logger.info("GETTING AVAILABLE CONFIG-MAPS FROM '{}' NAMESPACE".format(namespace.upper()))
    if (configmaps_object.items != []):
        for configmap in configmaps_object.items:
            configmaps_list.append(configmap.metadata.name)
    else:
        logger.debug("No configmaps available in {} namespace".format(namespace))
    return configmaps_list
        

def create_configmap(api_group, namespace, resource_definition, logger):
    configmap_metadata = resource_definition["metadata"]
    configmap_name = configmap_metadata["name"]

    deployed_configmaps = list_configmaps(api_group=api_group, namespace=namespace, logger=logger)
    logger.info("Deployed ConfigMaps are: {}".format(deployed_configmaps))

    # Verifying the namespace before deploying
    if ("namespace" in configmap_metadata) and (configmap_metadata["namespace"] != namespace):
        logger.info("The configmap can only be deployed to '{}' namespace, (namespace in resource definition: '{}')" \
                    "fixing the namespace in the resource definition".format(namespace, configmap_metadata["namespace"]))
        resource_definition["metadata"]["namespace"] = namespace
        logger.info("Updated Resource defintion for configmap: {}".format(resource_definition))
    
    # Creating New ConfigMap or Updating if already deployed
    if (configmap_name not in deployed_configmaps):
        logger.info("'{}' not available configmaps list, deploying it".format(configmap_name))
        try:
            logger.info("Deploying '{}' configmap in '{}' namespace".format(configmap_name, namespace))
            response = api_group.create_namespaced_config_map(body=resource_definition, namespace=namespace)
            logger.info("ConfigMap '{}' created successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
    else:
        logger.info("'{}' already available in the configmaps list, patching it with latest resource definition".format(configmap_name))
        try:
            response = api_group.replace_namespaced_config_map(name=configmap_name ,body=resource_definition, namespace=namespace)
            logger.info("ConfigMap '{}' replaced successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
            logger.error("ConfigMap configurations cannot be modified, please delete the configmap and create again.")