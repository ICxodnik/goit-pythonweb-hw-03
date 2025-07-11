
FROM python:3.13-slim

WORKDIR /web_app

COPY requirements.txt /web_app/

RUN pip install --no-cache-dir -r /web_app/requirements.txt

COPY . /web_app/

EXPOSE 3000

CMD ["watchmedo", "auto-restart", "--directory=.", "--pattern=*.py", "--recursive", "python", "server.py"]
