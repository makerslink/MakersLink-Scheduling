# Ubuntu 24.04 LTS (Python 3.12), pinned so every build starts from the same base.
FROM ubuntu:24.04

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata ca-certificates sqlite3 libsqlite3-dev python3 python3-pip python3-virtualenv && \
  rm -rf /var/lib/apt/lists/*

RUN echo "Europe/Stockholm" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# The app runs as this unprivileged user. The db/ and pks/ directories that
# are mounted into the container must be writable by uid 10001 (see README).
RUN groupadd --system --gid 10001 scheduling && \
  useradd --system --uid 10001 --gid scheduling --no-create-home --shell /usr/sbin/nologin scheduling

WORKDIR /scheduling

# .dockerignore keeps .git, local databases and other non-app files out.
COPY . /scheduling

# Install into a virtual environment so the system Python is left alone.
ENV VIRTUAL_ENV=/opt/python/virtualenv
RUN virtualenv $VIRTUAL_ENV --python=python3
ENV PATH=$VIRTUAL_ENV/bin:$PATH
RUN pip install --no-cache-dir -r requirements.txt

# Port gunicorn listens on; Traefik reaches it over the Docker network.
EXPOSE 8000

ENV DJANGO_ENV=prod

WORKDIR /scheduling/makerslink

# Collect static files for WhiteNoise. collectstatic needs no real secret.
RUN DJANGO_SECRET=collectstatic-only python manage.py collectstatic --noinput

# Only the database and service-account key directories are written at runtime.
RUN mkdir -p /scheduling/pks && \
  chown scheduling:scheduling /scheduling/makerslink/makerslink/db /scheduling/pks

USER scheduling

CMD ["./start-server.sh"]
