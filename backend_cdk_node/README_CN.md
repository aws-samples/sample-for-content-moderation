# 部署步骤

[English version of the document](README.md)

## 前提条件 ❗ ❗ ❗ 

在需要部署的区域需提前申请Bedrock中的Nova/Claude权限


## 1. 创建初始环境

本方案有两种部署方式。支持X86与ARM架构，默认配置为X86架构。

### 1.1 部署方式1-部署X86架构方案
在AWS控制台搜索并进入CloudShell服务，切换到us-west-2区域

### 1.2 部署方式2-部署ARM架构方案
如果需要部署ARM，需创建一个64位arm架构Amazon Linux 2023系统的EC2实例。

[创建ARM部署环境](CreateEC2_CN.md)

如需部署ARM架构，需要在cdk.json中修改Architecture参数为arm


## 2.下载代码 ❗ 

通用版本请通过git下载，定制版本请手动上传安装包。

### 2.1.下载代码方式1-Git


git clone git@github.com:aws-samples/sample-for-content-moderation.git


### 2.2.下载代码方式2-手动上传

如果使用的是CloudShell，请在CloudShell右上角选择上传文件。然后解压缩。

```
unzip xxxxxx.zip
```

如果使用EC2，请使用以下代码将代码包手动上传到EC2中,然后解压缩

```
scp -i xxx.pem xxxxxx.zip ec2-user@xxxxx.us-west-2.compute.amazonaws.com:/home/ec2-user/

ssh -i "xxx.pem" ec2-user@xxxxxxxx.us-west-2.compute.amazonaws.com

unzip xxxxxx.zip

```



## 3. 安装依赖与修改配置文件  ❗ 

进入部署目录，并安装cdk依赖

```bash

cd content_moderation/backend_cdk_node

npm install 
```


修改`cdk.json`中的配置：


- #deploy_type（可选）

 ```
"deploy_type":[1,2,3,4,5]
```

deploy_type为部署类型， 1为文本审核，2为图片审核，3为音频审核，4为视频审核，5为直播审核


- ❗#AWS账号ID  （必填）
```
"account_id": "xxxxxxxxxx"
```


- #Region  （可选）

```
"region_name": "us-west-2"
```


- 测试账号用户ID （可选） ❗ 
```
"user_id": "lee"
```

- 图像审核的方式（可选）  ❗  ❗  ❗ 

```
"visual_moderation_type":"image"

#可选值为image及video。
image为将视频切分为图片然后进行审核。
video为将视频切分为短视频通过llm进行审核。
```




- 文本审核模型（可选）

```
"text_model_id": "anthropic.claude-3-sonnet-20240229-v1:0"

```

- 图片审核模型（可选） ❗  ❗  ❗ 

```
"img_model_id":"us.amazon.nova-lite-v1:0"

如果需要rekognition 审核，此次可配置为rekognition

```


- 短视频审核模型（可选） ❗  ❗  ❗ 

*如果图像审核的方式选择了bedrock,请进行配置
```
"video_model_id":"us.amazon.nova-pro-v1:0"
```

  
- VPC CIDR（可选）

```
默认值为 "10.0.0.0/16"
```

- Architecture（可选）❗ ❗ ❗

```
默认值为 "x86"
可选值为 x86、arm

如需使用arm请修改此配置
```

- ECR仓库名称  （可选） ❗
```
"repository_name": "moderation_repository"
```
如修改了此参数，请在后续执行镜像构建时指定新仓库名称。

- 测试账号回调URL（可选）
```
"callback_url": "http://xxxxx.com/callback"
```

如果需要结果推送到指定服务器，需配置链接。并在lamnda_callback中实现回调逻辑。


- 文件可读有效期（可选）❗❗❗

```
"file_expiration_time": "3600",
```

所有上传到S3指定目录中的文件，均配置了加密后的临时访问连接。 您可配置访问链接可读的有效时间(秒)。
最大值为3600秒(6小时)

## 4. 上传镜像，配置推送（可选）

如果只需要文本审核或图片审核。可调过本步骤

如果需要音频审核、视频审核、直播审核，需要进行镜像的上传。


## 4.1 修改Dockerfile文件

本项目依赖于python与ffmpeg.您可选择使用已经构建好的基础镜像，或手动构建镜像。

### 4.1.1 使用预构建的基础镜像❗❗❗

请将content_modetaion/backend/Dockerfile文件中的首行修改为

```
FROM public.ecr.aws/x9b0z9r8/ffmpeg6_python311_boto3:v01
```

### 4.1.2 手动构建基础镜像

请参考 [构建Docker基础镜像](../backend/README_DOCKER_CN.md)

请将content_modetaion/backend/Dockerfile文件中的首行修改为自己构建的基础镜像。


## 4.2 创建镜像仓库并上传本地代码❗❗❗

请填写AWS账号/区域信息，并执行以下语句。
如在cdk.json中自定义过仓库名称，请同步修改下面语句中的仓库名称。

```bash
#bash ecr.sh <aws-account-id> <region> <repository-name> <dockerfile-path>

bash ecr.sh xxxxxxxx us-west-2 moderation_repository ../backend/
```


## 5. 部署CDK ❗


然后在EC2中执行以下命令
```bash
cdk bootstrap

cdk deploy
```


## 6.使用方法


### 6.1 文本审核/图片审核/直播审核

  查看输出值

  - TestToken = Your token 

  其中TestToken的值为api中所需的token (本方案的用户模块仅用于方案测试，请勿直接用于生产环境)
  
  - ContentModeration16.ModerationApiEndpoint6FEA6CEF = https://ewwcrippi5.execute-api.us-west-2.amazonaws.com/api/
  
  其中ModerationApiEndpoint即为文本审核/图片审核/直播审核所需的请求链接
  
  文本审核和图片审核结果实时返回
  
  直播审核结果可到Dynamodb中查看
  
  使用方法见backend中的README.MD [使用说明文档](../backend/README_CN.md)


### 6.2 音频审核/视频审核

  查看输出值
  
  ContentModeration16.S3BucketName = contentmoderation16-moderations3bucketb3c8798d-k2kgrnnpisch
  
  其S3BucketName即为音频/视频存储桶的名称
  
  请在存储桶中创建 s3_audio_moderation、s3_video_moderation文件夹
  
  然后将需要审核的音频文件放入 s3_audio_moderation 、需要审核的视频文件放入 s3_video_moderation
  
  审核结果可到Dynamodb中查看



## 重要声明 ❗ ❗ ❗ 
```
本项目为示例项目，仅用于演示如何使用 AWS 进行内容审核。  

该项目未经过生产环境验证，请勿直接用于生产环境。  
```  