FROM continuumio/miniconda3

ADD . /app
WORKDIR /app

RUN conda env create -f /app/environment.yml

CMD python /app/main.py
