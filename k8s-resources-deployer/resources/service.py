import os
import yaml
import json
from kubernetes.client import exceptions


def list_services(api_group, namespace, logger):
    services_list = []
    services_object = api_group.list_namespaced_service(namespace=namespace)
    logger.info("GETTING AVAILABLE SERVICES FROM '{}' NAMESPACE".format(namespace.upper()))
    if (services_object.items != []):
        for service in services_object.items:
            services_list.append(service.metadata.name)
    else:
        logger.debug("No services available in {} namespace".format(namespace))
    return services_list
        

def create_service(api_group, namespace, resource_definition, logger):
    service_metadata = resource_definition["metadata"]
    service_name = service_metadata["name"]

    deployed_services = list_services(api_group=api_group, namespace=namespace, logger=logger)
    logger.info("Deployed Services are: {}".format(deployed_services))

    # Verifying the namespace before deploying
    if ("namespace" in service_metadata) and (service_metadata["namespace"] != namespace):
        logger.info("The service can only be deployed to '{}' namespace, (namespace in resource definition: '{}')" \
                    "fixing the namespace in the resource definition".format(namespace, service_metadata["namespace"]))
        resource_definition["metadata"]["namespace"] = namespace
        logger.info("Updated Resource defintion for service: {}".format(resource_definition))
    
    # Creating New Service or Updating if already deployed
    if (service_name not in deployed_services):
        logger.info("'{}' not available in services list, deploying it".format(service_name))
        try:
            logger.info("Deploying '{}' service in '{}' namespace".format(service_name, namespace))
            response = api_group.create_namespaced_service(body=resource_definition, namespace=namespace)
            logger.info("Service '{}' created successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
    else:
        logger.info("'{}' already available in the services list, patching it with latest resource definition".format(service_name))
        try:
            response = api_group.patch_namespaced_service(name=service_name ,body=resource_definition, namespace=namespace)
            logger.info("Service '{}' patched successfully".format(response.metadata.name))
        except exceptions.ApiException as error:
            error_body = json.loads(error.body)
            logger.error(error_body["message"])
            logger.error("Service configurations cannot be modified, please delete the service and create again.")