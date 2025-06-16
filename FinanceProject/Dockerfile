FROM python:3.10-bullseye
# Python docker images: https://github.com/docker-library/docs/tree/master/python/

USER root


COPY backend/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY main.py ./app/
COPY backend/ ./app/backend
WORKDIR /app/

