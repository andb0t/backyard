FROM heroku/heroku:18-build

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# -- Install Pipenv:
RUN apt update && apt upgrade -y && apt install python3.7-dev -y
RUN curl --silent https://bootstrap.pypa.io/get-pip.py | python3.7

# Backwards compatility.
RUN rm -fr /usr/bin/python3 && ln /usr/bin/python3.7 /usr/bin/python3

RUN pip3 install pipenv

COPY . /app
WORKDIR /app

RUN pipenv install --skip-lock
RUN pipenv run python setup.py develop

EXPOSE 8080

ENTRYPOINT [ "pipenv", "run", "python" ]
CMD [ "src/backyard/api" ]