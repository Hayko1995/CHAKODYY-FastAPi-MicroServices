FROM python:3.11

RUN apt-get update
RUN apt-get install libgdal-dev -y 
RUN apt install gdal-bin python3-gdal -y
RUN pip install --upgrade pip
RUN pip install numpy
# RUN pip install gdal

ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/
