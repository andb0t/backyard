FROM python:3.6-alpine as base

FROM base as build
RUN apk add --no-cache build-base
RUN python3 -m venv /venv

ADD . /project
RUN /venv/bin/pip install --upgrade pip && /venv/bin/pip install /project

FROM base
COPY --from=build /venv /venv

RUN adduser -D -u 9989 app
USER app
ENV PYTHONDONTWRITEBYTECODE=x

CMD ["/venv/bin/python3", "-m", "backyard.api"]
