# Use an official Python runtime as a parent image
FROM ubuntu

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ca-certificates
RUN apt-get install -y sqlite3 libsqlite3-dev
RUN apt-get install -y python3 python3-pip

# Set the working directory to /scheduling
WORKDIR /scheduling

# Copy the current directory contents into the container at /app
ADD . /scheduling

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Go into djano dir
WORKDIR /scheduling/makerslink

# Run app.py when the container launches
#CMD ["/bin/bash"]
CMD ./start-server.sh
