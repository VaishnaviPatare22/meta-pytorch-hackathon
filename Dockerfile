# --- Base Image ---
FROM python:3.10-slim

# --- Set working directory ---
WORKDIR /app

# --- Copy files ---
COPY . /app

# --- Install dependencies ---
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Expose port ---
EXPOSE 7860

# --- Start FastAPI server ---
CMD ["uvicorn", "inference:app", "--host", "0.0.0.0", "--port", "7860", "--reload"]