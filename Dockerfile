FROM nikolaik/python-nodejs:python3.9-nodejs15 AS builder

WORKDIR /opt/app

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system


FROM nikolaik/python-nodejs:python3.9-nodejs15-slim

ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY . ./

RUN npm install -g nodemon

CMD ["pipenv", "run", "dev"]
