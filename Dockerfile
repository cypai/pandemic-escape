FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /app

WORKDIR /app

RUN rm /app/main.py
RUN pip3 install -r requirements.txt
