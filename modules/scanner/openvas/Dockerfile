FROM kalilinux/kali-linux-docker as base
RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y python3.6 python3-venv net-tools psmisc lsof redis openvas

# update redis server configs
RUN echo 'unixsocket /var/run/redis-openvas/redis-server.sock' >> /etc/redis/redis.conf
# TODO: check if 766 is proper
RUN echo 'unixsocketperm 766' >> /etc/redis/redis.conf
RUN sed -i.bak 's/bind 127.0.0.1 ::1/bind 127.0.0.1/g' /etc/redis/redis.conf
RUN mkdir /var/run/redis-openvas/
# TODO: check if 777 is proper
RUN chmod -R 777 /var/run/redis-openvas/
RUN service redis-server restart

RUN openvas-setup
RUN openvassd
RUN openvasmd
RUN gsad

FROM base as build
RUN /usr/bin/python3.6 -m venv /venv
RUN /venv/bin/pip install --upgrade pip
RUN /bin/bash -c 'source /venv/bin/activate'
RUN /venv/bin/pip install python-gvm

ADD . /project
RUN /venv/bin/pip install /project

FROM base
COPY --from=build /venv /venv
COPY entrypoint.sh /entrypoint
ENTRYPOINT ["/entrypoint"]

RUN adduser --disabled-password --gecos "" -u 9989 app
USER app
ENV PYTHONDONTWRITEBYTECODE=x
ENV TZ=Europe/Berlin

CMD ["/venv/bin/python3", "-m", "backyard.module.openvas"]