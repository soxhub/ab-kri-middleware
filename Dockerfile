FROM python:3.8-alpine

RUN apk add --update alpine-sdk
RUN mkdir -p /app
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements/requirements.txt --trusted-host pypi.python.org

CMD ["sh", "-c", "python app/services/simple_fetch/main.py -f app/services/simple_fetch/config.yml -s galaxy"]
