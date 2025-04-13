# Building a Base Image with Python and FFmpeg

## Create a Dockerfile

```dockerfile
FROM python:3.11-alpine

LABEL authors="tedli"

# Install ffmpeg
RUN apk add --no-cache ffmpeg

# Set working directory
WORKDIR /app

# Copy requirements.txt into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set default command
CMD ["/bin/sh"]
```

## Build a Multi-Architecture Image

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ffmpeg6_python311_m:v01 .
```

## Tag the Image

```bash
docker tag ffmpeg6_python311_m:v01 yyyyyy/ffmpeg6_python311_m:v01
```

## Push to Remote Repository

```bash
docker push yyyyyy/ffmpeg6_python311_m:v01
```
