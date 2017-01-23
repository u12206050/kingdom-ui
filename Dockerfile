# nginx-gunicorn-flask

FROM ubuntu:12.04
MAINTAINER Ekansh Singh <ekansh.singh@opscale.io>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get install -y python python-pip python-virtualenv nginx gunicorn supervisor

# Setup flask application
RUN mkdir -p /deploy/main
COPY main /deploy/main
RUN pip install -r /deploy/main/requirements.txt

# Setup nginx
RUN rm /etc/nginx/sites-enabled/default
COPY flask.conf /etc/nginx/sites-available/
RUN ln -s /etc/nginx/sites-available/flask.conf /etc/nginx/sites-enabled/flask.conf
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Setup supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY gunicorn.conf /etc/supervisor/conf.d/gunicorn.conf

# Start processes
CMD ["/usr/bin/supervisord"]
