from python:3.8-alpine

# create app directory
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src/main.py ./

CMD ["python", "-u", "main.py"]
