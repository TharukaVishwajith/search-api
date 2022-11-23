FROM python:3.7.7-slim-buster

# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY . .

EXPOSE 80
CMD [ "gunicorn","-w","2","-b","0.0.0.0:80","app:create_app()"]
