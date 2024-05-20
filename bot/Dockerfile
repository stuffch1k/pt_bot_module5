# FROM python:3.10-alpine



FROM python:3.11-slim
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY bot.py bot.py
CMD ["python", "bot.py"]
