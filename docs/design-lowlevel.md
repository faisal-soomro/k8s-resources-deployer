# k8s-resources-deployer Low Level Design
This document describes the Low Level Design of the `k8s-resources-deployer` i.e the design about the application itself and what approaches are used while developing it. 

## k8s-resources-deployer
The application is python based solution which provides a very simple web based form for users to provide kubernetes resources definition in the form of yaml. The tool, in turn parses the yaml definition and does the following:

- Figures out the resource type from the parsed yaml and calls the relevant method for deploying kubernetes resources. The currently kubernetes supported resources are:
  - Pod
  - Deployment
  - Service
  - Config Map
  - Secret
- The tool also checks for the if the namespace is provided in the resource definition and takes the following decisions:
  - If the namespace is not provided, the tool will pass the resource definition for further processing.
  - If the namespace in the resource definition matches the allowed namespace for deploying the resource, the tool will pass the resource definition for further processing.
  - If the namespace differs from the allowed namespace, the application will output the warning message on the webpage about the namepsace being different than the allowed one. The tool then replaces the namespace in the resource definition and passes the updated resource definition for further processing.
- The tool will process the resource definition received after namespace verification and proceed with resource deployment.
  - If the resource to be deployed is not available in the namespace, then it created.
  - If the resource to be deployed is already available in the namespace, then it is updated with the latest resource definition.
- If the resource creation/upgradation is successful, the the success message will be printed on the webpage, otherwise the error logs will be displayed for further investigations.

The diagram below describes the the design along with explaining what role each part in the diagram is playing to make this solution complete:

![current-infra](diagrams/lld.jpg)


