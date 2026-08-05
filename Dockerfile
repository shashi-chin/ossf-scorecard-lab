# INTENTIONAL: unpinned Docker base image for Pinned-Dependencies education.
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
