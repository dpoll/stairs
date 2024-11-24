# Use the official Python 2.7 image from the Docker Hub
FROM python:2.7

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the file
COPY leaderboard.py ./

# Install the requests library
RUN pip install --no-cache-dir requests

# Copy the rest of the application code into the container
COPY . .

# Set default environment variables (can be overridden at runtime)
# ENV GOOGLE_SHEETS_URL=https://example.com/default.csv
# ENV LOCAL_FILENAME=default.csv

# Run the script when the container launches
CMD ["python", "./leaderboard.py"]
