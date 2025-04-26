# Content Moderation

## 1.文本审核/图片审核/直播审核 使用说明

部署CDK后查看输出值

ContentModeration16.ModerationApiEndpoint6FEA6CEF = https://xxxxxx.execute-api.us-west-2.amazonaws.com/api/

其中ModerationApiEndpoint即为文本审核/图片审核/直播审核所需的请求链接

文本审核和图片审核结果实时返回

直播审核结果可到Dynamodb中查看

### 1.1 查询单个音频/视频/直播审核任务的状态

`curl` 测试链接：

```bash
curl --location 'https://xxxxxx/api/query_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "url":""
}'
```

请求头

| 参数名     | 类型     | 是否必填 | 描述            |
|---------|--------|------|---------------|
| user_id | String | 是    | 用户在 AWS 的唯一标识 |
| token   | String | 是    | 用户在 AWS 的密钥   |

请求体

| 参数名        | 类型     | 是否必填 | 描述      | 示例值                    |
|------------|--------|------|---------|------------------------|
| url        | String | 是    | 视频URL   | https://xxxxxxxxx.m3u8 |
| start_time | Long   | 否    | 起始时间时间戳 | 1745665852000          |
| end_time   | Long   | 否    | 停止时间时间戳 | 1745695859000          |


### 1.2 提交音频/视频/直播审核任务

`curl` 测试链接：

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

请求头

| 参数名     | 类型     | 是否必填 | 描述            |
|---------|--------|------|---------------|
| user_id | String | 是    | 用户在 AWS 的唯一标识 |
| token   | String | 是    | 用户在 AWS 的密钥   |

请求体

| 参数名                    | 类型     | 是否必填 | 描述                                                                      | 示例值                                       |
|------------------------|--------|------|-------------------------------------------------------------------------|-------------------------------------------|
| url                    | String | 是    | 视频URL                                                                   | https://xxxxxxxxx.m3u8                    |
| video_interval_seconds | Int    | 否    | 视频截取频率，每隔x秒截取一次。取值范围为1-25                                               | 10                                        |
| image_interval_seconds | Int    | 否    | 图片截取频率，每隔x秒截取一次。取值范围为1-100                                              | 1                                         |
| audio_interval_seconds | Int    | 否    | 音频截取频率：音频持续x秒后进行截取。取值范围为1-25                                            | 10                                        |
| text_model_id          | String | 是    | 文本审核模型id                                                                | us.anthropic.claude-3-haiku-20240307-v1:0 |
| visual_moderation_type | String | 是    | 审核方式。可选值为image和video。配置image后将对直播进行截图，然后进行审核。配置video后将对直播进行视频截取，然后进行审核。 | image                                     |
| img_model_id           | String | 是    | 图片审核模型id                                                                | us.amazon.nova-lite-v1:0                  |
| video_model_id         | String | 是    | 视频审核模型id                                                                | us.amazon.nova-pro-v1:0                   |
| save_flag              | Int    | 是    | 文件保存标识。1是保持全部文件，0为仅保存违规内容。                                              | 1                                         |

### 1.3 文本审核

`curl` 测试链接：

```bash
curl --location 'https://xxxxxx/api/text_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "text":"打你的头"
}'


curl --location 'https://xxxxxx/api/text_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "text":"打你的头"
}'


```

请求头

| 参数名     | 类型     | 是否必填 | 描述            |
|---------|--------|------|---------------|
| user_id | String | 是    | 用户在 AWS 的唯一标识 |
| token   | String | 是    | 用户在 AWS 的密钥   |

请求体

| 参数名      | 类型     | 是否必填 | 描述                            | 示例值            |
|----------|--------|------|-------------------------------|----------------|
| text     | String | 是    | 需要审核的文本内容                     | 今天天气真好         |
| prompt   | String | 否    | 用于引导模型分析的提示词                  | 请判断是否违规内容      |
| model_id | String | 否    | 模型 ID，支持 nova/claude，需提供具体 ID | claude-3-haiku |

见：[AWS Bedrock 模型支持](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

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

### 1.4 图片审核

`curl` 测试链接：

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

请求头

| 参数名     | 类型     | 是否必填 | 描述            |
|---------|--------|------|---------------|
| user_id | String | 是    | 用户在 AWS 的唯一标识 |
| token   | String | 是    | 用户在 AWS 的密钥   |

请求体

| 参数名        | 类型     | 是否必填 | 描述                                      | 示例值            |
|------------|--------|------|-----------------------------------------|----------------|
| type       | Int    | 是    | 1 为使用 Rekognition 审核，2 为使用 Bedrock 进行审核 | 1              |
| img_base64 | String | 是    | 图片的 base64 值                            | （base64字符串）    |
| prompt     | String | 否    | 选填提示词，用于引导模型分析                          |                |
| model_id   | String | 否    | 模型 ID，支持 nova/claude，需提供具体 ID           | nova-lite-v1:0 |

见：[AWS Bedrock 模型支持](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

```
us.amazon.nova-lite-v1:0
us.amazon.nova-pro-v1:0	
anthropic.claude-3-sonnet-20240229-v1:0	
anthropic.claude-3-5-sonnet-20240620-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0	
us.anthropic.claude-3-7-sonnet-20250219-v1:0	

```

### 1.5 离线音频审核/视频审核 使用说明

部署CDK后查看输出值

ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch

其S3BucketName即为音频/视频存储桶的名称

请在存储桶中创建 s3_audio_moderation、s3_video_moderation文件夹

然后将需要审核的音频文件放入 s3_audio_moderation 、需要审核的视频文件放入 s3_video_moderation

审核结果可到Dynamodb中查看



