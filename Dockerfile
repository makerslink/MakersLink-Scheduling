# Use an official Python runtime as a parent image
FROM ubuntu

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata ca-certificates sqlite3 libsqlite3-dev python3 python3-pip python3-virtualenv

RUN echo "Europe/Stockholm" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# Set the working directory to /scheduling
WORKDIR /scheduling

# Copy the current directory contents into the container at /app
ADD . /scheduling

# Create and activate virtual enviroment to not impact systemt pyton.
ENV VIRTUAL_ENV /opt/python/virtualenv
RUN virtualenv $VIRTUAL_ENV --python=python3
ENV PATH $VIRTUAL_ENV/bin:$PATH

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DJANGO_ENV=prod

# Go into djano dir
WORKDIR /scheduling/makerslink

# Run app.py when the container launches
#CMD ["/bin/bash"]
CMD ./start-server.sh
