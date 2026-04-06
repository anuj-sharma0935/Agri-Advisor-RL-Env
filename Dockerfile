FROM python:3.9-slim

WORKDIR /code

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY . .

# Sabse pehle purani library saaf karo aur fresh versions dalo
RUN pip install --no-cache-dir --upgrade pip && \
    pip uninstall -y huggingface_hub && \
    pip install --no-cache-dir huggingface_hub==0.20.3 gradio==4.44.1 fastapi uvicorn gymnasium numpy

EXPOSE 7860

CMD ["python", "app.py"]