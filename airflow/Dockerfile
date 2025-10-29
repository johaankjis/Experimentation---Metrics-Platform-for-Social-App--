# Dockerfile for Airflow with experiment platform dependencies

FROM apache/airflow:2.8.1-python3.11

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs and source code
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root src /opt/airflow/src
COPY --chown=airflow:root config /opt/airflow/config
