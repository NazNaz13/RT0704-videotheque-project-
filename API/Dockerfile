FROM python:3

WORKDIR /app

COPY api.py .
COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt
VOLUME /app
EXPOSE 5051

CMD ["python3", "api.py" ]