FROM python:alpine

COPY ./k8s-resources-deployer /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "/app/app.py"]