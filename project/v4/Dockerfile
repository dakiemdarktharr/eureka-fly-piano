FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglfw3 && rm -rf /var/lib/apt/lists/*
COPY project/v4/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY project /app/project
ENV FLYPIANO_V4_STATE=/state
RUN useradd -m -u 10001 appuser && mkdir -p /state /app/project/v4/results && chown appuser:appuser /state /app/project/v4/results
USER appuser
EXPOSE 8878
CMD ["python", "project/v4/app.py", "--no-browser", "--host", "0.0.0.0"]
