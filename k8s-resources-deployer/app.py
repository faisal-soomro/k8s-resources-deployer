#! /usr/bin/env python3

import sys
import os
import io
import logging
import configparser
from traceback import print_exc
from kubernetes import client, config
from resources import yaml_parser, deployer
from flask import Flask, render_template, request



# Setting logging configurations
log_level = logging.INFO
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, level=log_level)
log = logging.getLogger()

log_capture_string = io.StringIO()
console_handler = logging.StreamHandler(log_capture_string)
console_handler_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s EOL")
console_handler.setFormatter(console_handler_formatter)
console_handler.setLevel(logging.WARN)
log.addHandler(console_handler)



# Reading from config.ini
try:
    config_file = configparser.ConfigParser()
    config_file.read("config.ini")
    kubernetes_section = config_file["kubernetes"]
except :
    print_exc()
    log.error("Failed to load config.ini, Please verify the config.ini and try again, exiting...")
    sys.exit(-1)



# Loading kubernetes configurations
try:
    if os.getenv('KUBERNETES_SERVICE_HOST'):
        config.load_incluster_config()
        namespace_path = kubernetes_section["namespace_path_inside_pod"]
        with open(namespace_path) as file:
            namespace = file.read().strip()
            file.close()
        if (namespace != ""):
            log.info("Fetched namespace value as {} from {}".format(namespace, namespace_path))
        else:
            log.error("Namespace is not fetched successfully and cannot proceed further, exiting...")
            sys.exit(-1)
    else:
        config.load_kube_config()
        namespace = kubernetes_section["namespace"]
        if (namespace != ""):
            log.info("Fetched namespace value as {} from configurations file".format(namespace))
        else:
            log.error("Namespace is not fetched successfully and cannot proceed further, exiting...")
            sys.exit(-1)

    # Loading Api Resource Groups for kubernetes resources
    v1 = client.CoreV1Api()
    appsv1 = client.AppsV1Api()
except :
    print_exc()
    log.error("Failed to load configurations, exiting...")
    sys.exit(-1)



# Creating Flask Configurations
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        yaml_string = request.form.get("yaml-definition")
        log.debug("Received Data: {}".format(yaml_string))
        parsed_yaml = yaml_parser.parse_string(yaml_string=yaml_string, logger=log)
        if (parsed_yaml != -1):
            response = deployer.deploy_resource(parsed_yaml=parsed_yaml, logger=log, log_capture_string=log_capture_string,
                                                api_v1=v1, api_apps_v1=appsv1, namespace=namespace)
            return render_template('index.html', title="k8s-resource-deployer", namespace=namespace, response=response)
        else:
            response="Unable to parse yaml resource, please verify and deploy again"
            return render_template('index.html', title="k8s-resource-deployer", namespace=namespace, response=response)
    return render_template('index.html', title="k8s-resource-deployer", namespace=namespace)



# Defining and calling main() method
def main():
    # app.debug = True
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()