FROM python:3.11-slim

RUN apt-get update && apt-get install -y graphviz

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]