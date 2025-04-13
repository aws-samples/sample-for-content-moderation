# Deployment Steps

[中文文档](README_CN.md)

## Prerequisites ❗ ❗ ❗

You must request access to Nova/Claude in Bedrock in the region where the deployment will take place.

## 1. Create Initial Environment

There are two deployment methods for this solution. It supports both X86 and ARM architectures, with the default configuration set to X86 architecture.

### 1.1 Deployment Method 1 - Deploying X86 Architecture Solution
Search for and access the CloudShell service in the AWS Console, and switch to the us-west-2 region.

### 1.2 Deployment Method 2 - Deploying ARM Architecture Solution
If you need to deploy ARM, you need to create a 64-bit ARM architecture Amazon Linux 2023 EC2 instance.

[Create ARM Deployment Environment](CreateEC2_CN.md)

To deploy ARM architecture, modify the Architecture parameter in the `cdk.json` file to `arm`.

## 2. Download Code ❗

For the generic version, download it via git, or manually upload the installation package for the customized version.

### 2.1 Download Code via Git

```bash
git clone git@github.com:aws-samples/sample-for-content-moderation.git
```

### 2.2 Manual Upload of Code

If using CloudShell, click on the "Upload File" option in the top right corner of CloudShell and then unzip the package.

```bash
unzip xxxxxx.zip
```

If using EC2, upload the code package to EC2 using the following commands, then unzip it:

```bash
scp -i xxx.pem xxxxxx.zip ec2-user@xxxxx.us-west-2.compute.amazonaws.com:/home/ec2-user/

ssh -i "xxx.pem" ec2-user@xxxxxxxx.us-west-2.compute.amazonaws.com

unzip xxxxxx.zip
```

## 3. Install Dependencies and Modify Configuration Files ❗

Navigate to the deployment directory and install the CDK dependencies.

```bash
cd content_moderation/backend_cdk_node

npm install
```

Modify the `cdk.json` configuration file:

- #deploy_type (Optional)

```
"deploy_type": [1, 2, 3, 4, 5]
```

`deploy_type` indicates the deployment type. `1` is for text moderation, `2` is for image moderation, `3` is for audio moderation, `4` is for video moderation, and `5` is for live-stream moderation.

- ❗ #AWS Account ID (Required)

```
"account_id": "xxxxxxxxxx"
```

- #Region (Optional)

```
"region_name": "us-west-2"
```

- Test Account User ID (Optional) ❗

```
"user_id": "lee"
```

- Image Moderation Type (Optional) ❗ ❗ ❗

```
"visual_moderation_type": "image"
```

The possible values are `image` and `video`. If `image` is selected, the video is split into images for moderation. If `video` is selected, the video is cut into short videos and then moderated by LLM.

- Image Moderation Plugin (Optional)

```
"image_moderation_plugin": "Possible values are bedrock or rekognition"
```

- Text Moderation Model (Optional)

```
"text_model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
```

- Image/Short Video Moderation Model (Optional) ❗ ❗ ❗

*If you selected `bedrock` for image moderation, configure it here:*

```
"img_model_id": "us.amazon.nova-lite-v1:0"
```

- If moderating short videos, use `us.amazon.nova-pro-v1:0`.
- If moderating images, use `us.amazon.nova-lite-v1:0`.

- VPC CIDR (Optional)

```
"vpc_cidr": "10.0.0.0/16"
```

- Architecture (Optional) ❗

```
"architecture": "x86"
```

The default is `x86`. Possible values are `x86` and `arm`. If you are using ARM, change this configuration.

- ECR Repository Name (Optional) ❗

```
"repository_name": "moderation_repository"
```

If this parameter is modified, specify the new repository name when building the image later.

- Test Account Callback URL (Optional)

```
"callback_url": "http://xxxxx.com/callback"
```

If you need results pushed to a specific server, configure the URL and implement the callback logic in `lambda_callback`.

- File Read Expiration Time (Optional) ❗ ❗ ❗

```
"file_expiration_time": "604800"
```

All files uploaded to the specified S3 directory are configured with encrypted temporary access links. You can configure how long the link will be valid (in seconds). The maximum value is 604800 seconds (7 days).

## 4. Upload Images, Configure Push (Optional)

If only text or image moderation is required, you can skip this step.

If audio, video, or live-stream moderation is needed, image uploading is required.

## 4.1 Modify Dockerfile

This project depends on Python and FFmpeg. You can either use a pre-built base image or manually build your own image.

### 4.1.1 Use Pre-built Base Image ❗ ❗ ❗

Modify the first line of the `content_moderation/backend/Dockerfile` file to:

```bash
FROM public.ecr.aws/x9b0z9r8/ffmpeg6_python311_boto3:v01
```

### 4.1.2 Manually Build Base Image

Please refer to [Build Docker Base Image](../backend/README_DOCKER_CN.md) for more details.

Modify the first line of the `content_moderation/backend/Dockerfile` file to use your own built base image.

## 4.2 Create Image Repository and Upload Local Code ❗ ❗ ❗

Fill in the AWS account/region information and execute the following command.

If you customized the repository name in `cdk.json`, also modify the repository name in the following command.

```bash
# bash ecr.sh <aws-account-id> <region> <repository-name> <dockerfile-path>

bash ecr.sh xxxxxxxx us-west-2 moderation_repository ../backend/
```

## 5. Deploy CDK ❗

Then, execute the following commands in EC2:

```bash
cdk bootstrap

cdk deploy
```

## 6. Usage

### 6.1 Text Moderation/Image Moderation/Live-Stream Moderation

View the output values:

- `TestToken = Your token`

The value of `TestToken` is the token required for the API (the user module in this solution is only for testing and should not be used in production).

- `ContentModeration16.ModerationApiEndpoint6FEA6CEF = https://ewwcrippi5.execute-api.us-west-2.amazonaws.com/api/`

`ModerationApiEndpoint` is the request link required for text moderation/image moderation/live-stream moderation.

Text and image moderation results are returned in real-time.

Live-stream moderation results can be viewed in DynamoDB.

For more details, refer to the usage instructions in the `backend/README.md` [Usage Documentation](../backend/README_CN.md).

### 6.2 Audio Moderation/Video Moderation

View the output values:

- `ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch`

The `S3BucketName` is the name of the audio/video storage bucket.

Create `s3_audio_moderation` and `s3_video_moderation` folders in the bucket.

Place the audio files to be moderated in `s3_audio_moderation` and the video files in `s3_video_moderation`.

Moderation results can be viewed in DynamoDB.

## Important Disclaimer ❗ ❗ ❗

```
This project is a sample project, primarily to demonstrate how to use AWS for content moderation.

This project has not been validated in production environments, so do not use it directly in production.
```