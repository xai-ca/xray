# Use an official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (including Graphviz)
RUN apt-get update && apt-get install -y graphviz

# Copy and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Dash will run on
EXPOSE 8050

# Run the Dash app
CMD ["python", "app.py"]
