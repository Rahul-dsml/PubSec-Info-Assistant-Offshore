# Use the official Python 3.10.7 image as the base
FROM python:3.10.7

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt first (improves caching)
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy everything else
COPY . /app/

# Command to run your application
CMD ["uvicorn", "app:app", "--port", "8050"]