FROM python:3.7-alpine

RUN apk add --no-cache python3-dev curl gnupg build-base

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt

COPY . /code/

CMD ["python3", "/code/ocean_worker.py"]
