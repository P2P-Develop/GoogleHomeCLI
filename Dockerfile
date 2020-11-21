FROM python:3.9 AS builder

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv \
 && pipenv install --system


FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY . ./

CMD ["python", "src/home.py"]
