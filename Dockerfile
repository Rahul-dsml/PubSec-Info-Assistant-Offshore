# Use the official Python 3.10.7 image as the base
FROM python:3.10.7

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./backend

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8050"]
