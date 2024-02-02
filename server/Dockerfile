FROM python:3

WORKDIR /app

COPY app.py .
COPY requirements.txt .
COPY users.json .


RUN pip install --no-cache-dir -r requirements.txt
VOLUME /app
EXPOSE 5050

CMD ["python3", "app.py" ]