# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Run app.py when the container launches
ENTRYPOINT ["python", "FileServer.py"]


