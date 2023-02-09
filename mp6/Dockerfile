# Implement This
FROM python:3.9

COPY mp6 /mp6
COPY mp2 /mp2

WORKDIR /mp6

RUN ls

RUN apt update &&\
    apt install -y pip &&\
    pip install flask &&\
    ls &&\
    chmod +x ./docker/entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["./docker/entrypoint.sh"]