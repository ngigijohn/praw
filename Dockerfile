FROM python:latest

SHELL ["/bin/bash", "-c"]

WORKDIR /praw

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get upgrade -y && \
    pip install -r ./requirements.txt

COPY . .

VOLUME ./logs

CMD ["python", "main.py"]