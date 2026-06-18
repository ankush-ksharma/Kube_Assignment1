# Step 1: Use a lightweight, secure Python base image
FROM python:3.11-slim

# Step 2: Establish the internal directory for our application files
WORKDIR /app

# Step 3: Copy only the dependencies file first to maximize build caching
COPY requirements.txt .

# Step 4: Install the Python packages without saving temporary installer files
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your Python application code into the image container space
COPY app.py .

# Step 6: Inform the container runtime which network port your app listens to
EXPOSE 3000

# Step 7: Define the command executed when the container starts up
CMD ["python", "app.py"]