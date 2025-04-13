FROM public.ecr.aws/docker/library/python:3.10-slim

LABEL authors="author"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "__main__.py"]