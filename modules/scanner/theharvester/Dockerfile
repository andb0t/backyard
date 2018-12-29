# FROM python:3.6-alpine as base
FROM kalilinux/kali-linux-docker as base
RUN apt-get update
RUN apt-get install -y python3.6 python3-venv theharvester

FROM base as build
RUN /usr/bin/python3.6 -m venv /venv
RUN /venv/bin/pip install --upgrade pip

ADD . /project
RUN /venv/bin/pip install /project

FROM base
COPY --from=build /venv /venv
# COPY entrypoint.sh /entrypoint
# ENTRYPOINT ["sh", "/entrypoint"]

RUN adduser --disabled-password --gecos "" -u 9989 app
USER app
ENV PYTHONDONTWRITEBYTECODE=x
ENV TZ=Europe/Berlin

CMD ["/venv/bin/python3", "-m", "backyard.module.theharvester"]
