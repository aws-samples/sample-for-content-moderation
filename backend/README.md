# Content Moderation

## 1. Text/Image/Live Moderation – Usage Guide

After deploying the CDK, check the output value:

```
ContentModeration16.ModerationApiEndpoint6FEA6CEF = https://xxxxxx.execute-api.us-west-2.amazonaws.com/api/
```

The `ModerationApiEndpoint` is the base URL for all text, image, and live moderation requests.

- **Text and image moderation results** are returned in real-time.
- **Live moderation results** can be viewed in **DynamoDB**.

---

### 1.1 Query a Specific Audio/Video/Live Moderation Task

Example using `curl`:

```bash
curl --location 'https://xxxxxx/api/query_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "url":""
}'
```

- `user_id`: Required  
- `token`: Required  
- `url`: Required

---

### 1.2 Submit Audio/Video/Live Moderation Task

Example using `curl`:

```bash
curl --location 'https://xxxxxx/api/submit_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "url":"https://xxxxxx/xxx/93.mp4"
}'
```

- `user_id`: Required  
- `token`: Required  
- `url`: Required

---

### 1.3 Text Moderation

Example using `curl`:

```bash
curl --location 'https://xxxxxx/api/text_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "text":"Some text to moderate"
}'
```

Parameters:

- `text`: Required  
- `prompt`: Optional  
- `model_id`: Optional. Supports nova/claude models. For full list, see [AWS Bedrock Supported Models](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

Supported model IDs:
```
us.amazon.nova-lite-v1:0
us.amazon.nova-micro-v1:0	
us.amazon.nova-pro-v1:0	
us.anthropic.claude-3-haiku-20240307-v1:0	
us.anthropic.claude-3-sonnet-20240229-v1:0	
us.anthropic.claude-3-5-haiku-20241022-v1:0	
us.anthropic.claude-3-5-sonnet-20240620-v1:0
us.anthropic.claude-3-5-sonnet-20241022-v2:0	
```

---

### 1.4 Image Moderation

Example using `curl`:

```bash
curl --location 'https://xxxxxx/api/img_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "type": 2,
    "img_base64": "........"
}'
```

Parameters:

- `type`: Required – `1` for Rekognition, `2` for Bedrock  
- `img_base64`: Required – Base64 string of the image  
- `prompt`: Optional  
- `model_id`: Optional – Supports nova/claude models (see [AWS Bedrock Supported Models](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html))

Supported model IDs:
```
us.amazon.nova-lite-v1:0
us.amazon.nova-pro-v1:0	
anthropic.claude-3-sonnet-20240229-v1:0	
anthropic.claude-3-5-sonnet-20240620-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0	
```

---

### 1.5 Offline Audio/Video Moderation – Usage Guide

After deploying the CDK, check the output value:

```
ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch
```

The `S3BucketName` is the name of the S3 bucket used for storing audio and video files.

Please create the following folders in the bucket:

- `s3_audio_moderation` – For uploading audio files to be moderated
- `s3_video_moderation` – For uploading video files to be moderated

Moderation results will be stored in **DynamoDB**.

---

## 2. Project Structure

### `__main__.py` – Entry point

This file starts the service and listens to SQS for moderation tasks.

### `listener` – Event Listeners

- `sqs_listener`: Listens to SQS messages

### `plugin` – Plugins

- `rekogition_image_moderation`: Image moderation using Rekognition  
- `bedrock_image_moderation`: Image moderation using Bedrock  
- `bedrock_text_moderation`: Text moderation using Bedrock  
- `sagemaker_asr`: Audio transcription using SageMaker ASR

### `scanner` – File Scanners

- `file_scanner`: Scans local files

### `processor` – Message Processors

- `sqs_msg_processor`: Processes SQS messages  
- `video_processor`: Processes video-related tasks  
- `content_moderation`: Moderates image and audio content  
- `save_info_alert`: Saves info and sends alerts

### `tools` – Utility Library

### `lambda` – AWS Lambda Functions

- `lambda_text_moderation`: Handles text moderation  
- `lambda_img_moderation`: Handles image moderation  
- `lambda_query`: Queries moderation task status  
- `lambda_submit`: Submits audio/video/live moderation tasks  
- `lambda_callback`: Sends alerts  
- `lambda_init_info`: CDK initialization  
- `lambda_daemon`: Monitors SQS status
