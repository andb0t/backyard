FROM python:3.6

# use pip caching (COPYs and ADDs in this order!)
COPY requirements.txt /
WORKDIR /
RUN pip install -r requirements.txt

# now add the rest
ENV TZ=Europe/Berlin

COPY app.py /
COPY analysis.py /

CMD ["python", "app.py"]
