FROM python:3.6

WORKDIR /home

RUN apt-get update && apt-get install ffmpeg -y

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD python app.py