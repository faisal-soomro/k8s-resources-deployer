import os
import yaml
import json
from kubernetes.client import exceptions


def list_deployments(api_group, namespace, logger):
    deployments_list = []
    deployments_object = api_group.list_namespaced_deployment(namespace=namespace)
    logger.info("GETTING AVAILABLE DEPLOYMENTS FROM '{}' NAMESPACE".format(namespace.upper()))
    if (deployments_object.items != []):
        for deployment in deployments_object.items:
            deployments_list.append(deployment.metadata.name)
    else:
        logger.info("No deployments available in {} namespace".format(namespace))
    return deployments_list


def create_deployment(api_group, namespace, resource_definition, logger):
    deployment_metadata = resource_definition["metadata"]
    deployment_name = resource_definition["metadata"]["name"]

    deployed_deployments = list_deployments(api_group=api_group, namespace=namespace, logger=logger)
    logger.info("Deployed Deployments are: {}".format(deployed_deployments))

    # Verifying the namespace before deploying
    if ("namespace" in deployment_metadata) and (deployment_metadata["namespace"] != namespace):
        logger.warn("The deployment can only be deployed to '{}' namespace, (namespace in resource definition: '{}')" \
                    "fixing the namespace in the resource definition".format(namespace, deployment_metadata["namespace"]))
        resource_definition["metadata"]["namespace"] = namespace
        logger.warn("Updated Resource defintion for deployment: {}".format(resource_definition))

    # Creating New Deployment or Updating if already deployed
    if (deployment_name not in deployed_deployments):
        logger.info("'{}' not available deployments list, deploying it".format(deployment_name))
        try:
            logger.debug("Deploying '{}' deployment in '{}' namespace".format(deployment_name, namespace))
            response = api_group.create_namespaced_deployment(body=resource_definition, namespace=namespace)
            logger.info("Deployment '{}' created successfully".format(response.metadata.name))
            return("Deployment '{}' created successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
    else:
        logger.info("'{}' already available in the deployments list, patching it with latest resource definition".format(deployment_name))
        try:
            response = api_group.patch_namespaced_deployment(name=deployment_name ,body=resource_definition, namespace=namespace)
            logger.info("Deployment '{}' patched successfully".format(response.metadata.name))
            return("Deployment '{}' patched successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
            logger.error("Deployment configurations cannot be modified, please delete the deployment and create again.")