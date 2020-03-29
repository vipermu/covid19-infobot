FROM continuumio/miniconda3

WORKDIR /app

ADD ./environment.yml /app/environment.yml
RUN conda env create -f /app/environment.yml
SHELL ["conda", "run", "-n", "covid19-infobot", "/bin/bash", "-c"]

RUN echo 'Make sure that covid19-infobot environment is activated:'
RUN python -c "import telegram"

ADD ./main.py .
ADD ./utils ./utils

ENTRYPOINT ["conda", "run", "-n", "covid19-infobot", "python3", "main.py"]