FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /work/project
COPY environment.lock .
RUN pip install --no-cache-dir -r environment.lock
COPY . .
ENV OPENBLAS_NUM_THREADS=1
CMD ["python", "reproduce.py", "core"]
