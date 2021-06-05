FROM python:3.9

COPY ./k8s-resources-deployer /app
WORKDIR /app

RUN pip install -r requirements.txt