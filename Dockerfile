FROM python:latest

SHELL ["/bin/bash", "-c"]

WORKDIR /praw

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install build-essential libpoppler-cpp-dev pkg-config python3-dev -y && \
    pip install -r ./requirements.txt

COPY . .

CMD ["python", "main.py"]

