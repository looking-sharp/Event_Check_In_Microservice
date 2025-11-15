FROM python:3.9-slim-buster
WORKDIR /Event_Check_In_Microservice
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "app.py"]