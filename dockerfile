FROM ubuntu
RUN apt-get update && apt-get upgrade -y
ENV TZ=""

WORKDIR /code

#Update Repos
RUN apt-get update
RUN apt-get upgrade -y

#Install Dependencies
RUN apt-get install python3-pymssql -y
RUN apt-get install python3-pip -y
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install ffmpeg

#Make work on ARM
RUN apt-get install libffi-dev
RUN apt-get -y install cmake protobuf-compiler

#Copy pip requirements & Install
COPY master/requirements.txt .
RUN pip install -r requirements.txt

#Copy Code
COPY master/ .

#Start Bot
CMD ["python3", "-u", "main.py"]
