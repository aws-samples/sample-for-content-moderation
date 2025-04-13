# Create Deployment Environment  

[中文文档](CreateEC2_CN.md)  

## 1. Create a Policy  

In the AWS console, search for **IAM**, click **Policies**, and create a new policy.  
Select the **EC2** service.  
Switch to the **JSON** editor mode and replace the content with the following permissions:  

```json
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

Enter **DeployContentModerationPolicy** as the policy name, then click **Create Policy**.  

## 2. Create a Role  

1. In the **IAM** page, click **Roles**, then click **Create Role**.  
2. Select **AWS Service**, then choose **EC2**.  
3. In the **Permissions** section, enter and select **DeployContentModerationPolicy**, then click **Next**.  
4. Set the **Role Name** to **DeployContentModerationRole**.  
5. Click **Create Role**.  

## 3. Create an EC2 Instance  

1. In the AWS console, search for **EC2**, and select a region (e.g., `us-west-2`).  
2. Create an EC2 instance with the following settings:  

    ```plaintext
    OS: Amazon Linux 2023  
    Architecture: 64-bit ARM  
    Instance Type: c8g.large  
    Advanced Details - IAM Instance Profile: DeployContentModerationRole  
    ```  

3. When creating an EC2 **key pair** for the first time, it will be automatically downloaded to your **Downloads** folder.  
4. Set appropriate permissions for the key pair:  

    ```bash
    chmod 400 xxx.pem
    ```  

## 4. Initialize the EC2 Deployment Environment  

1. Connect to the EC2 instance:  

    ```bash
    ssh -i "xxx.pem" ec2-user@xxxxxxxx.us-west-2.compute.amazonaws.com
    ```  

2. Run the following commands to install required dependencies:  

    ```bash
    # Install Docker
    sudo dnf install -y docker
    sudo systemctl enable --now docker
    sudo usermod -aG docker ec2-user  # Allow non-root users to use Docker

    # Install Python
    sudo dnf install -y python3 python3-pip

    # Install Node.js (LTS version)
    sudo dnf install -y nodejs npm

    # Install AWS CDK
    sudo npm install -g aws-cdk
    ```  