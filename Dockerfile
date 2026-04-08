FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Expose the port for the validator/ping
EXPOSE 7860

# Command to run your Streamlit UI (as the server)
CMD ["streamlit", "run", "server/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]