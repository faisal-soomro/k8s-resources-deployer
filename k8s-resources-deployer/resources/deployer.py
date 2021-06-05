from resources import pod, deployment, service, configmap, secret
from traceback import print_exc


def deploy_resource(parsed_yaml, logger, log_capture_string, api_v1, api_apps_v1, namespace):
    response = None
    try:
        logger.info("Resource type is {}, deploying it...".format(parsed_yaml["kind"]))

        # Checking for the resource kind before deploying it
        if parsed_yaml["kind"].lower() == "pod":
            logger.debug("Resource defintion for pod: {}".format(parsed_yaml))
            response = pod.create_pod(api_group=api_v1, namespace=namespace, resource_definition=parsed_yaml, logger=logger)
        elif parsed_yaml["kind"].lower() == "deployment":
            logger.debug("Resource defintion for deployment: {}".format(parsed_yaml))
            response = deployment.create_deployment(api_group=api_apps_v1, namespace=namespace, resource_definition=parsed_yaml, logger=logger)
        elif parsed_yaml["kind"].lower() == "service":
            logger.debug("Resource defintion for service: {}".format(parsed_yaml))
            response = service.create_service(api_group=api_v1, namespace=namespace, resource_definition=parsed_yaml, logger=logger)
        elif parsed_yaml["kind"].lower() == "configmap":
            logger.debug("Resource defintion for configmap: {}".format(parsed_yaml))
            response = configmap.create_configmap(api_group=api_v1, namespace=namespace, resource_definition=parsed_yaml, logger=logger)
        elif parsed_yaml["kind"].lower() == "secret":
            logger.debug("Resource defintion for secret: {}".format(parsed_yaml))
            response = secret.create_secret(api_group=api_v1, namespace=namespace, resource_definition=parsed_yaml, logger=logger)
        else:
            logger.error("Unsupported resource definition, please select the resource kind from the following: [pod, deployment, service, configmap, secret]")


    except:
        print_exc()
        logger.error("Failed to get valid kubernetes configurations, please verify the configurations and try again")

    # Fething the logs from I/O Stream to be shown into html page
    log_contents = log_capture_string.getvalue().split("EOL")
    log_capture_string.truncate(0)

    print(log_contents)
    # Appending the response fetched from the previous function call to show it along with other logs on html page
    if (response != None) and (response != ""):
        log_contents.append(response)
    

    return(log_contents)



    
    