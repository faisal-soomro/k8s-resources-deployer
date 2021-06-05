import os
import yaml
import json
from kubernetes.client import exceptions


def list_secrets(api_group, namespace, logger):
    secrets_list = []
    secrets_object = api_group.list_namespaced_secret(namespace=namespace)
    logger.info("GETTING AVAILABLE SECRETS FROM '{}' NAMESPACE".format(namespace.upper()))
    if (secrets_object.items != []):
        for secret in secrets_object.items:
            secrets_list.append(secret.metadata.name)
    else:
        logger.debug("No secrets available in {} namespace".format(namespace))
    return secrets_list
        

def create_secret(api_group, namespace, resource_definition, logger):
    secret_metadata = resource_definition["metadata"]
    secret_name = secret_metadata["name"]

    deployed_secrets = list_secrets(api_group=api_group, namespace=namespace, logger=logger)
    logger.info("Deployed secrets are: {}".format(deployed_secrets))

    # Verifying the namespace before deploying
    if ("namespace" in secret_metadata) and (secret_metadata["namespace"] != namespace):
        logger.warn("The secret can only be deployed to '{}' namespace, (namespace in resource definition: '{}')" \
                    "fixing the namespace in the resource definition".format(namespace, secret_metadata["namespace"]))
        resource_definition["metadata"]["namespace"] = namespace
        logger.warn("Updated Resource defintion for secret: {}".format(resource_definition))
    
    # Creating New secret or Updating if already deployed
    if (secret_name not in deployed_secrets):
        logger.info("'{}' not available secrets list, deploying it".format(secret_name))
        try:
            logger.debug("Deploying '{}' secret in '{}' namespace".format(secret_name, namespace))
            response = api_group.create_namespaced_secret(body=resource_definition, namespace=namespace)
            logger.info("Secret '{}' created successfully".format(response.metadata.name))
            return("Secret '{}' created successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
    else:
        logger.info("'{}' already available in the secrets list, patching it with latest resource definition".format(secret_name))
        try:
            response = api_group.replace_namespaced_secret(name=secret_name ,body=resource_definition, namespace=namespace)
            logger.info("Secret '{}' replaced successfully".format(response.metadata.name))
            return("Secret '{}' replaced successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
            logger.error("Secret configurations cannot be modified, please delete the secret and create again.")