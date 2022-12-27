FROM python:3.10.6

WORKDIR /usr/src/parking
COPY requirements.txt /usr/src/parking
RUN pip3 install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
