FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 FLYPIANO_STATE=/state
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libegl1 libglfw3 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY project/v3/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY project/simulation /app/project/simulation
COPY project/connectome_manifest.json /app/project/connectome_manifest.json
COPY project/v2/world.py project/v2/simulate.py /app/project/v2/
COPY project/v2/ui/vendor /app/project/v2/ui/vendor
COPY project/v2/assets /app/project/v2/assets
COPY project/v3 /app/project/v3
RUN useradd --create-home --uid 10001 flypiano && mkdir -p /state /app/project/connectome /app/project/v2/data /app/project/v2/scores/private && chown -R flypiano:flypiano /state
USER flypiano
EXPOSE 8877
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8877/api/health',timeout=3)"
CMD ["python","project/v3/app.py","--host","0.0.0.0","--no-browser"]
