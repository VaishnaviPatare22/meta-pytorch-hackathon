FROM python:3.9

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .


ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true

# Expose the correct port
EXPOSE 7860

# Run the app
CMD ["streamlit", "run", "server/app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]