FROM python:3.9-slim

WORKDIR /opt/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel &&\
pip install --no-cache-dir -r  /requirements.txt

COPY . /opt/src/app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]