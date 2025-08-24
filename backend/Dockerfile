FROM public.ecr.aws/x9b0z9r8/ffmpeg6_python311_boto3:v01

LABEL authors="author"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "__main__.py"]