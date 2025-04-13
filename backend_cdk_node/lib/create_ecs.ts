import {
  CfnOutput,
  aws_iam as iam,
  aws_ecs as ecs,
  aws_ec2 as ec2,
  aws_logs as logs,
  aws_ecr as ecr,
  RemovalPolicy,
  Stack,
  Tags
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as uuid from 'uuid';
import { BackendCdkStack } from './backend_cdk_stack';
import { NagSuppressions } from 'cdk-nag';

export function createEcs(stack: BackendCdkStack) {
  const vpc = new ec2.Vpc(stack, "Moderation-VPC", {
    ipAddresses: ec2.IpAddresses.cidr(stack.node.tryGetContext('vpcCidr') || "10.111.0.0/16"),
    maxAzs: 2,
    natGateways: 1,
    subnetConfiguration: [
      {
        name: "Public",
        subnetType: ec2.SubnetType.PUBLIC,
        cidrMask: 20
      },
      {
        name: "Private",
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        cidrMask: 20
      }
    ]
  });



  // 创建一个 CloudWatch 日志组，用于存储 VPC 流日志
  const logGroupVPC = new logs.LogGroup(stack, "VPCFlowLogGroup", {
    logGroupName: `/aws/vpc/flow-logs-${stack.stackName}-${uuid.v4().slice(0, 8)}`, // 使用 stackName 确保唯一性
    retention: logs.RetentionDays.ONE_WEEK, // 根据需求设置日志保留期限
  });

  const customCloudWatchLogsPolicy = new iam.Policy(stack, 'CustomCloudWatchLogsPolicy', {
    statements: [
      new iam.PolicyStatement({
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents",
          "logs:GetLogEvents",
          "logs:FilterLogEvents"
        ],
        resources: [
          logGroupVPC.logGroupArn,
        ]
      })
    ]
  });

  const logRole = new iam.Role(stack, 'Moderation-ECS-LogRole', {
    assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
  });
  logRole.attachInlinePolicy(customCloudWatchLogsPolicy)

  // 启用 VPC 流日志
  new ec2.CfnFlowLog(stack, "Moderation-VPCFlowLog", {
    resourceId: vpc.vpcId,
    resourceType: "VPC",
    trafficType: "ALL", // 捕获所有流量，你可以选择 "ACCEPT", "REJECT" 或 "ALL"
    logDestinationType: "cloud-watch-logs",
    logGroupName: logGroupVPC.logGroupName,
    deliverLogsPermissionArn: logRole.roleArn
  });

  vpc.addInterfaceEndpoint("ECRDockerEndpoint", {
    service: ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER
  });
  vpc.addInterfaceEndpoint("ECREndpoint", {
    service: ec2.InterfaceVpcEndpointAwsService.ECR
  });

  const privateSubnets = vpc.privateSubnets;

  const securityGroup = new ec2.SecurityGroup(stack, "Moderation-ECS-SecurityGroup", {
    vpc,
    description: "Security group for Moderation ECS tasks",
    allowAllOutbound: false
  });

  securityGroup.addEgressRule(
    ec2.Peer.anyIpv4(),
    ec2.Port.tcp(443),
    'Allow HTTPS outbound traffic'
  );

  securityGroup.addEgressRule(
    ec2.Peer.anyIpv4(),
    ec2.Port.tcp(80),
    'Allow HTTP outbound traffic'
  );

  securityGroup.addEgressRule(
    ec2.Peer.anyIpv4(),
    ec2.Port.udp(53),
    'Allow DNS (UDP) outbound traffic'
  );
  securityGroup.addEgressRule(
    ec2.Peer.anyIpv4(),
    ec2.Port.tcp(53),
    'Allow DNS (TCP) outbound traffic'
  );



  const cluster = new ecs.Cluster(stack, "Moderation-ECS-Cluster", {
    vpc,
    containerInsights: true
  });

  const executionRole = new iam.Role(stack, "Moderation-ECS-TaskExecutionRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    managedPolicies: []
  });



  const logGroupz = new logs.LogGroup(stack, "MyECSLogGroup", {
    logGroupName: `/aws/ecs/ecs-log-group-${stack.stackName}-${uuid.v4().slice(0, 8)}`, // 使用 stackName 确保唯一性
    retention: logs.RetentionDays.ONE_WEEK
  });

  const ecrRepository = ecr.Repository.fromRepositoryName(stack, "Moderation-ECR-Repository", stack.repositoryName);


  executionRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "ecr:GetAuthorizationToken",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ],
    resources: [logGroupz.logGroupArn, ecrRepository.repositoryArn]
  }));

  NagSuppressions.addResourceSuppressions(executionRole, [
    {
      id: 'AwsSolutions-IAM5',
      reason: 'Explicit actions have been defined for this policy, ensuring appropriate permissions are granted.',
    }
  ], true);



  const taskRole = new iam.Role(stack, "Moderation-ECS-TaskRole", {
    assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com")
  });



  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:SendMessage"
    ],
    resources: [stack.moderationQueueArn, stack.callbackQueueArn, stack.s3ModerationQueueArn].filter(Boolean)
  }));

  

  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
    ],
    resources: [`${stack.s3Arn}`, `${stack.s3Arn}/*`]
  }));

  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:BatchWriteItem",
      "dynamodb:BatchGetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ],
    resources: [stack.taskTable.tableArn, stack.taskDetailTable.tableArn, stack.userInfoTable.tableArn,
      stack.taskTable.tableArn+"/index/TaskIdQueryIndex", stack.taskDetailTable.tableArn+"/index/TaskIdQueryIndex", stack.userInfoTable.tableArn+"/index/TaskIdQueryIndex"
    ]
  }));


  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "sagemaker:InvokeEndpoint"
    ],
    resources: [stack.sagemakerEndpointArn]
  }));

  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "rekognition:DetectLabels",
      "rekognition:DetectFaces",
      "rekognition:DetectModerationLabels",
      "rekognition:CompareFaces"
    ],
    resources: [`*`]
    // resources: [`arn:aws:rekognition:${stack.regionName}:${stack.accountId}:*`]
  }));

  taskRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "bedrock:InvokeModel",
      "bedrock:ListFoundationModels",
    ],
    resources: [
      "arn:aws:bedrock:*::foundation-model/*",
      `arn:aws:bedrock:*:${stack.accountId}:inference-profile/*`
    ]
    // resources: ["*"]
  }));


  NagSuppressions.addResourceSuppressions(taskRole, [
    {
      id: 'AwsSolutions-IAM5',
      reason: 'ECS  requires access to all objects in the S3 bucket for content moderation processing.',
      appliesTo: [`Resource::${stack.s3Arn}/*`], 
    },
    {
      id: 'AwsSolutions-IAM5',
      reason: 'Rekognition and Bedrock require access to a wide range of resources, using wildcards to simplify permissions.',
      appliesTo: [
        'Action::rekognition:DetectLabels',
        'Action::rekognition:DetectFaces',
        'Action::rekognition:DetectModerationLabels',
        'Action::rekognition:CompareFaces',
        `Resource::*`,
      ]
    },    {
      id: 'AwsSolutions-IAM5',
      reason: 'Rekognition and Bedrock require access to a wide range of resources, using wildcards to simplify permissions.',
      appliesTo: [
        'Action::bedrock:InvokeModel',
        'Action::bedrock:ListFoundationModels',
        'Resource::arn:aws:bedrock:*::foundation-model/*',
        `Resource::arn:aws:bedrock:*:${stack.accountId}:inference-profile/*`,
      ]
    }
  ], true);


  const logGroup = new logs.LogGroup(stack, "Moderation-ECS-LogGroup", {
    retention: logs.RetentionDays.ONE_WEEK,
    removalPolicy: RemovalPolicy.DESTROY
  });

  const taskDefinition = new ecs.FargateTaskDefinition(stack, "Moderation-ECS-TaskDefinition", {
    memoryLimitMiB: 2048,
    cpu: 1024,
    executionRole,
    taskRole,
    runtimePlatform: {
      operatingSystemFamily: ecs.OperatingSystemFamily.LINUX,
      cpuArchitecture: stack.node.tryGetContext("architecture") === 'x86'? ecs.CpuArchitecture.X86_64: ecs.CpuArchitecture.ARM64
    }
  });

  NagSuppressions.addResourceSuppressions(taskDefinition, [
    {
      id: "AwsSolutions-ECS2",
      reason: "Environment variables do not contain sensitive information."
    }
  ]);


  const container = taskDefinition.addContainer("Moderation-ECS-Container", {
    image: ecs.ContainerImage.fromEcrRepository(ecrRepository, "v01"),
    memoryLimitMiB: 2048,
    logging: ecs.LogDrivers.awsLogs({
      streamPrefix: "moderation",
      logGroup
    }),
    environment: {
      REGION_NAME: stack.region,
      PROGRAM_TYPE: "0",
      ATTEMPT_COUNT: "3",
      MODERATION_SQS: stack.moderationQueueUrl,
      CALLBACK_SQS: stack.callbackQueueUrl,
      S3_FILE_READABLE_EXPIRATION_TIME: stack.node.tryGetContext("file_expiration_time"),
      TASK_TABLE_NAME: stack.taskTable.tableName,
      TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
      MODERATION_BUCKET_NAME: stack.s3BucketName,
      S3BUCKET_CUSTOMER_DIR: "moderation_results",
      WHISPER_ENDPOINT_NAME: stack.sagemakerEndpointName,
      SPEECH_RECOGNIZER_PLUGIN :'sagemaker',
      TEXT_MODERATION_PLUGIN:'bedrock',
      VISUAL_MODERATION_TYPE :  stack.node.tryGetContext("visual_moderation_type"),
      IMAGE_MODERATION_PLUGIN :  stack.node.tryGetContext("image_moderation_plugin"),
      MODEL_ID:stack.node.tryGetContext("text_model_id"),
      IMG_MODEL_ID: stack.node.tryGetContext("img_model_id"),
      BATCH_PROCESS_IMG_NUMBER: "3",
      TAGS: stack.tagsJsonStr
    }
  });




  const service = new ecs.FargateService(stack, "Moderation-Service", {
    cluster,
    securityGroups: [securityGroup],
    taskDefinition,
    desiredCount: 1,
    minHealthyPercent: 50,
    enableECSManagedTags: true,
    propagateTags: ecs.PropagatedTagSource.SERVICE
  });

  new CfnOutput(stack, "ClusterName", {
    value: cluster.clusterName,
    description: "ECS Cluster Name"
  });

  new CfnOutput(stack, "ServiceName", {
    value: service.serviceName,
    description: "ECS Service Name"
  });

  stack.taskRole = taskRole
  stack.taskExecutionRole = executionRole
  stack.clusterName = cluster.clusterName
  stack.ecsArn = cluster.clusterArn
  stack.taskDefinitionArn = taskDefinition.taskDefinitionArn
  stack.containerName = container.containerName
  stack.securityGroupId = securityGroup.securityGroupId
  stack.privateSubnets = privateSubnets

}