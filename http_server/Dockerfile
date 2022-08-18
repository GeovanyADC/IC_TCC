FROM python:3.8.10

COPY . /code/app

WORKDIR /code/app

RUN pip install --no-cache-dir --upgrade -r /code/app/requirements.txt

CMD ["python3", "server.py"]

