from python:3.8-alpine

# create app directory
WORKDIR /app

COPY src/main.py ./
COPY requirements.txt ./
run pip install -r requirements.txt


CMD ["python", "-u", "main.py"]