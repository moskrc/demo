FROM python:3.5
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client gettext
ONBUILD RUN echo "America/Los_Angeles" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN mkdir -p /usr/src/logs
RUN mkdir -p /usr/src/app

RUN adduser --disabled-password --gecos '' msmuser
RUN chown -R msmuser:msmuser /usr/src/logs

ADD requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app

#ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

# Start uWSGI
CMD ["/usr/bin/gunicorn", "project.wsgi:application", "-w" ,"2","-b","8000"]
