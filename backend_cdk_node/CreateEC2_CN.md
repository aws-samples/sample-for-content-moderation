# 创建部署环境

[English version of the document](CreateEC2.md)


## 1.创建策略

控制台搜索IAM，点击【策略】，创建策略，选择服务【EC2】。
切换策略编辑器模式为【JSON】，复制以下权限进行替换。
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket",
                "s3:CreateBucket",
                "s3:PutEncryptionConfiguration",
                "s3:PutBucketPolicy",
                "s3:PutBucketPublicAccessBlock",
                "s3:PutBucketOwnershipControls",
                "s3:PutBucketVersioning",
                "s3:PutBucketTagging",
                "s3:PutLifecycleConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:PassRole",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "iam:DetachRolePolicy",
                "iam:PutRolePolicy",
                "iam:ListRoles",
                "iam:GetRole",
                "iam:TagRole",
                "iam:DeleteRolePolicy"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:PutImageTagMutability",
                "ecr:CreateRepository",
                "ecr:DeleteRepository",
                "ecr:DescribeRepositories",
                "ecr:PutLifecyclePolicy",
                "ecr:SetRepositoryPolicy",
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:TerminateInstances",
                "ec2:DescribeAvailabilityZones"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStacks",
                "cloudformation:UpdateStack",
                "cloudformation:DescribeStackEvents",
                "cloudformation:ListStacks",
                "cloudformation:CreateChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:DeleteChangeSet",
                "cloudformation:GetTemplate",
                "cloudformation:ValidateTemplate"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter",
                "ssm:PutParameter",
                "ssm:GetParameters",
                "ssm:DescribeParameters",
                "ssm:DeleteParameter"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:CreateQueue",
                "sqs:DeleteQueue",
                "sqs:SetQueueAttributes",
                "sqs:GetQueueAttributes",
                "sqs:TagQueue",
                "sqs:ListQueues",
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage"
            ],
            "Resource": "*"
        }
    ]
}
```
输入策略名称为DeployContentModerationPolicy
点击创建策略

## 2.创建角色

IAM页面点击【角色】，点击创建角色
选择【AWS服务】，选择【EC2】
权限策略中输入并选中【DeployContentModerationPolicy】，点击下一步
角色名称为【DeployContentModerationRole】
点击创建角色

## 3.创建EC2

控制台搜索EC2，并选择区域(例如us-west-2)
创建EC2
部分配置如下：

```
系统：Amazon Linux 2023
架构：64位arm
实例类型：c8g.large
高级详细信息-IAM 实例配置文件: DeployContentModerationRole
```

初次创建EC2 key pair时，会默认下载到本地Downloads文件夹
给予合适的权限 chmod 400 xxx.pem


## 4.初始化EC2部署环境

登录EC2
ssh -i "xxx.pem" ec2-user@xxxxxxxx.us-west-2.compute.amazonaws.com

执行以下代码
```
#安装 Docker
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user  # 让非 root 用户使用 Docker

#安装 Python
sudo dnf install -y python3 python3-pip

#安装 Node.js (LTS 版本)
sudo dnf install -y nodejs npm

#安装CDK
sudo npm install -g aws-cdk
```


