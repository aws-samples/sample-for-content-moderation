import * as iam from 'aws-cdk-lib/aws-iam';
import { BackendCdkStack } from './backend_cdk_stack';
import { AUDIO_MODERATION,  LIVE_MODERATION, VIDEO_MODERATION } from './config';
import { NagSuppressions } from 'cdk-nag';



export function createLambdaRole(stack: BackendCdkStack): iam.Role {
  const lambdaRole = new iam.Role(stack, "Moderation-LambdaRoleWithModeration", {
    assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com")
  });


  lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));


  lambdaRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "rekognition:DetectLabels",
      "rekognition:DetectFaces",
      "rekognition:DetectModerationLabels",
      "rekognition:CompareFaces"
    ],
    resources: ["*"]
    // resources: [`arn:aws:rekognition:${stack.regionName}:${stack.accountId}:*`]
  }));




  lambdaRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "bedrock:InvokeModel*",
      "bedrock:ListFoundationModels",
    ],
    resources: [
      "arn:aws:bedrock:*::foundation-model/*",
      `arn:aws:bedrock:*:${stack.accountId}:inference-profile/*`
    ]
    // resources: [
    // "*"
    // `arn:aws:bedrock::foundation-model/*`
    // ,
    // `arn:aws:bedrock:*:${stack.accountId}:inference-profile/*`
    // ]
  }));


  lambdaRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "s3:GetObject",
      "s3:PutObject"
    ],
    resources: [`${stack.s3Arn}/*`]
  }));


  if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => stack.deployType.includes(v))) {

    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        "sagemaker:InvokeEndpoint"
      ],
      resources: [stack.sagemakerEndpointArn]
    }));
    
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
      ],
      resources: [stack.moderationQueueArn, stack.callbackQueueArn, stack.s3ModerationQueueArn].filter(Boolean)
    }));

    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: [
        "ecs:RunTask",
        "ecs:StartTask",
        "ecs:StopTask",
        "ecs:DescribeTasks",
        "ecs:DescribeTaskDefinition",
        "ecs:TagResource"
      ],
      resources: [
         stack.ecsArn,
        `arn:aws:ecs:${stack.regionName}:${stack.accountId}:task/*/*`,
        `arn:aws:ecs:${stack.regionName}:${stack.accountId}:task-definition/*:*`
      ]
    }));

    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ["iam:PassRole"],
      resources: [stack.taskRole.roleArn,stack.taskExecutionRole.roleArn],
      conditions: {
        StringLike: {
          "iam:PassedToService": "ecs-tasks.amazonaws.com",
        }
      }
    }));
  }


  lambdaRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "lambda:UpdateFunctionConfiguration",
    ],
    resources: [`arn:aws:lambda:${stack.regionName}:${stack.accountId}:function:*`]
  }));


  lambdaRole.addToPolicy(new iam.PolicyStatement({
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
    resources: [
      stack.taskTable?.tableArn,
      stack.taskDetailTable?.tableArn,
      stack.userInfoTable?.tableArn,
      stack.taskTable?.tableArn ? stack.taskTable.tableArn + "/index/TaskIdQueryIndex" : null,
      stack.taskDetailTable?.tableArn ? stack.taskDetailTable.tableArn + "/index/TaskIdQueryIndex" : null,
      stack.userInfoTable?.tableArn ? stack.userInfoTable.tableArn + "/index/TaskIdQueryIndex" : null
    ].filter(Boolean)
  }));



  stack.lambdaRole = lambdaRole


  NagSuppressions.addResourceSuppressions(lambdaRole, [
    {
      id: 'AwsSolutions-IAM4',
      reason: 'Some actions require access to all resources. This is necessary for the function of the Lambda.',
      appliesTo: ['Policy::arn:<AWS::Partition>:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'],
    },
    {
      id: 'AwsSolutions-IAM5',
      reason: 'lambda update',
      appliesTo: [
        "Action::lambda:UpdateFunctionConfiguration",
        `Resource::arn:aws:lambda:${stack.regionName}:${stack.accountId}:function:*`
      ],
    },
    {
      id: 'AwsSolutions-IAM5',
      reason: 'ecs task definition',
      appliesTo: [
        "Action::ecs:RunTask",
        "Action::ecs:StartTask",
        "Action::ecs:StopTask",
        "Action::ecs:DescribeTasks",
        "Action::ecs:DescribeTaskDefinition",
        "Action::ecs:TagResource",
        `Resource::arn:aws:ecs:${stack.regionName}:${stack.accountId}:task/*/*`,
        `Resource::arn:aws:ecs:${stack.regionName}:${stack.accountId}:task-definition/*:*`
      ],
    },
    {
      id: 'AwsSolutions-IAM5',
      reason: 'Lambda function requires access to all objects in the S3 bucket for content moderation processing.',
      appliesTo: [
        "Action::s3:GetObject",
        "Action::s3:PutObject",
        `Resource::${stack.s3Arn}/*`
      ],
    },
    {
      id: 'AwsSolutions-IAM5',
      reason: "Environment variables do not contain sensitive information.",
      appliesTo: [
        'Action::rekognition:DetectLabels',
        'Action::rekognition:DetectFaces',
        'Action::rekognition:DetectModerationLabels',
        'Action::rekognition:CompareFaces',
        `Resource::*`,
      ]

    },
    {
      id: 'AwsSolutions-IAM5',
      reason: "Environment variables do not contain sensitive information.",
      appliesTo: [
        'Action::bedrock:InvokeModel*',
        'Action::bedrock:ListFoundationModels',
        "Resource::arn:aws:bedrock:*::foundation-model/*",
        `Resource::arn:aws:bedrock:*:${stack.accountId}:inference-profile/*`
      ]
    }
  ], true);

  return lambdaRole

}