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

- `user_id`：必填
- `token`：必填
- `url`：必填

### 1.2 提交音频/视频/直播审核任务

`curl` 测试链接：

```bash
curl --location 'https://xxxxxx/api/submit_moderation' \
--header 'user_id: [YOUR_USER_ID]' \
--header 'token: [YOUR_TOKEN]' \
--header 'Content-Type: application/json' \
--data '{
    "url":"https://xxxxxx/xxx/93.mp4"
}'
```

- `user_id`：必填
- `token`：必填
- `url`：必填

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

- `text`：必填
- `prompt`：选填
- `model_id`：选填，支持 nova/claude，具体 ID 见：[AWS Bedrock 模型支持](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

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

- `type`：必填，1 为使用 Rekognition 审核，2 为使用 Bedrock 进行审核。
- `img_base64`：必填，图片的 base64 值。
- `prompt`：选填
- `model_id`：选填，支持 nova/claude，具体 ID 见：[AWS Bedrock 模型支持](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/models-supported.html)

```
us.amazon.nova-lite-v1:0
us.amazon.nova-pro-v1:0	
anthropic.claude-3-sonnet-20240229-v1:0	
anthropic.claude-3-5-sonnet-20240620-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0	
```


### 1.5 离线音频审核/视频审核 使用说明

部署CDK后查看输出值

ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch

其S3BucketName即为音频/视频存储桶的名称

请在存储桶中创建 s3_audio_moderation、s3_video_moderation文件夹

然后将需要审核的音频文件放入 s3_audio_moderation 、需要审核的视频文件放入 s3_video_moderation

审核结果可到Dynamodb中查看





## 2.代码结构

`__main__.py` 启动类，监听 SQS 然后进行内容审核。

### listener 监听者

- `sqs_listener`：监听 SQS 消息。

### plugin 插件

- `rekogition_image_moderation`：Rekognition 图片审核。
- `bedrock_image_moderation`：Bedrock 图片审核。
- `bedrock_text_moderation`：Bedrock 文本审核。
- `sagemaker_asr`：SageMaker ASR。

### scanner 扫描器

- `file_scanner`：扫描本地文件。

### processor 处理器

- `sqs_msg_processor`：处理 SQS 消息。
- `video_processor`：处理视频消息。
- `content_moderation`：图片和音频审核。
- `save_info_alert`：保存信息并告警。

### tools 工具库

### lambda

- `lambda_text_moderation`：文本审核。
- `lambda_img_moderation`：图片审核。
- `lambda_query`：查询任务状态。
- `lambda_submit`：提交音频/视频/直播审核任务。
- `lambda_callback`：发送告警信息。
- `lambda_init_info`：CDK 初始化信息。
- `lambda_daemon`：监控 SQS 状态。
