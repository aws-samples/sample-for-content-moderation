# sample-for-content-moderation

## 1. Text/Image/Live Stream Moderation User Guide

After deploying the CDK, check the output values:

```
ContentModeration16.ModerationApiEndpoint6FEA6CEF = https://xxxxxx.execute-api.us-west-2.amazonaws.com/api/
```

The `ModerationApiEndpoint` is the endpoint URL required for text, image, and live stream moderation.

- **Text and image moderation** results are returned in real-time.
- **Live stream moderation** results can be viewed in **DynamoDB**.

### 1.1 Query Status of a Single Audio/Video/Live Moderation Task

Sample `curl` request:

```bash
curl --location 'https://xxxxxx/api/query_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "url":""
}'
```

**Request Headers**

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| user_id   | String | Yes      | Unique AWS user identifier     |
| token     | String | Yes      | AWS user access token          |

**Request Body**

| Parameter | Type   | Required | Description          | Example                        |
|-----------|--------|----------|----------------------|--------------------------------|
| url       | String | Yes      | Video URL            | https://xxxxxxxxx.m3u8         |
| start_time | Long   | 否    | Start time timestamp | 1745665852000          |
| end_time   | Long   | 否    | End time timestamp   | 1745695859000          |

---

### 1.2 Submit Audio/Video/Live Moderation Task

Sample `curl` request:

```bash
curl --location 'https://xxxxxx.execute-api.us-west-2.amazonaws.com/api/submit_moderation' \
--header 'user_id: xxxxxx' \
--header 'token: xxxxx-9a4c-42f5-b207-f1c9635a540c' \
--header 'Content-Type: application/json' \
--data '{
        "url":"https://xxxxxx/xxx/93.mp4",

        "video_interval_seconds": 10,
        "image_interval_seconds": 1,
        "audio_interval_seconds": 10,

        "text_model_id": "us.anthropic.claude-3-haiku-20240307-v1:0",
        "img_model_id": "us.amazon.nova-lite-v1:0",
        "video_model_id": "us.amazon.nova-pro-v1:0",

        "save_flag": 1,
        "visual_moderation_type": "image"
}'
```

**Request Headers**

| Parameter | Type   | Required | Description                |
|-----------|--------|----------|----------------------------|
| user_id   | String | Yes      | Unique AWS user identifier |
| token     | String | Yes      | AWS user access token      |

**Request Body**

| Parameter                | Type   | Required | Description                                                                 | Example                                      |
|--------------------------|--------|----------|-----------------------------------------------------------------------------|----------------------------------------------|
| url                      | String | Yes      | Video URL                                                                  | https://xxxxxxxxx.m3u8                       |
| video_interval_seconds   | Int    | No       | Frequency of video capture (every x seconds). Range: 1–25                  | 10                                           |
| image_interval_seconds   | Int    | No       | Frequency of image capture (every x seconds). Range: 1–100                 | 1                                            |
| audio_interval_seconds   | Int    | No       | Frequency of audio capture (after x seconds of audio). Range: 1–25        | 10                                           |
| text_model_id            | String | Yes      | Text moderation model ID                                                   | us.anthropic.claude-3-haiku-20240307-v1:0   |
| visual_moderation_type   | String | Yes      | Moderation type: `image` (screenshots) or `video` (video clips)           | image                                        |
| img_model_id             | String | Yes      | Image moderation model ID                                                  | us.amazon.nova-lite-v1:0                    |
| video_model_id           | String | Yes      | Video moderation model ID                                                  | us.amazon.nova-pro-v1:0                     |
| save_flag                | Int    | Yes      | Save flag: `1` for saving all, `0` for saving only violating content       | 1                                            |

---

### 1.3 Text Moderation

Sample `curl` request:

```bash
curl --location 'https://xxxxxx/api/text_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "text":"Hit your head"
}'
```

**Request Headers**

| Parameter | Type   | Required | Description                |
|-----------|--------|----------|----------------------------|
| user_id   | String | Yes      | Unique AWS user identifier |
| token     | String | Yes      | AWS user access token      |

**Request Body**

| Parameter  | Type   | Required | Description                                          | Example             |
|------------|--------|----------|------------------------------------------------------|---------------------|
| text       | String | Yes      | Text content to be moderated                         | It's a great day    |
| prompt     | String | No       | Prompt to guide the model analysis                   | Please check for violations |
| model_id   | String | No       | Model ID (supports nova/claude, specific ID needed)  | claude-3-haiku      |

See: [AWS Bedrock Model Support](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

```
us.amazon.nova-lite-v1:0
us.amazon.nova-micro-v1:0	
us.amazon.nova-pro-v1:0	
us.anthropic.claude-3-haiku-20240307-v1:0	
us.anthropic.claude-3-sonnet-20240229-v1:0	
us.anthropic.claude-3-5-haiku-20241022-v1:0	
us.anthropic.claude-3-5-sonnet-20240620-v1:0
us.anthropic.claude-3-5-sonnet-20241022-v2:0
us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

---

### 1.4 Image Moderation

Sample `curl` request:

```bash
curl --location 'https:/xxxxxx/api/img_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "type":2,
    "img_base64":"........"
}'
```

**Request Headers**

| Parameter | Type   | Required | Description                |
|-----------|--------|----------|----------------------------|
| user_id   | String | Yes      | Unique AWS user identifier |
| token     | String | Yes      | AWS user access token      |

**Request Body**

| Parameter    | Type   | Required | Description                                                    | Example          |
|--------------|--------|----------|----------------------------------------------------------------|------------------|
| type         | Int    | Yes      | `1` for Rekognition, `2` for Bedrock                           | 1                |
| img_base64   | String | Yes      | Base64-encoded image                                           | (base64 string)  |
| prompt       | String | No       | Prompt to guide the model analysis                             |                  |
| model_id     | String | No       | Model ID (supports nova/claude, specific ID needed)            | nova-lite-v1:0   |

See: [AWS Bedrock Model Support](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

```
us.amazon.nova-lite-v1:0
us.amazon.nova-pro-v1:0	
anthropic.claude-3-sonnet-20240229-v1:0	
anthropic.claude-3-5-sonnet-20240620-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0	
us.anthropic.claude-3-7-sonnet-20250219-v1:0	
```

---

### 1.5 Offline Audio/Video Moderation User Guide

After deploying the CDK, check the output values:

```
ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch
```

The `S3BucketName` is the name of the S3 bucket for storing audio/video files.

- Please create the following folders in the bucket:
  - `s3_audio_moderation` for audio files
  - `s3_video_moderation` for video files

- Upload the files to the corresponding folders.

- Moderation results can be viewed in **DynamoDB**.

