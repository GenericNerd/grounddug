FROM python:3

MAINTAINER Tyler Thompson "tyler@grounddug.xyz"

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt
RUN python3 -m spacy download en

COPY . /
COPY ./cogs /cogs

CMD [ "python3", "./grounddug.py" ]
