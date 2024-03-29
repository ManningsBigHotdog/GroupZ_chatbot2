FROM python:3.8

WORKDIR /usr/src/app

COPY . .
COPY config.ini /usr/src/app/config.ini

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV TELEGRAM_API_KEY=""

CMD ["python", "app.py"]