import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cr from 'aws-cdk-lib/custom-resources';
import * as uuid from 'uuid';
import * as lambdaEventSources from 'aws-cdk-lib/aws-lambda-event-sources';
import { BackendCdkStack } from './backend_cdk_stack';
import { CfnOutput } from 'aws-cdk-lib';
import { AUDIO_MODERATION, IMAGE_MODERATION, LIVE_MODERATION, TEXT_MODERATION, VIDEO_MODERATION } from './config';
import { NagSuppressions } from 'cdk-nag';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export function createLambda(stack: BackendCdkStack): void {

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



  const lambdaAuth = new lambda.Function(stack, "Moderation-Lambda-Auth", {
    runtime: lambda.Runtime.PYTHON_3_12,
    code: lambda.Code.fromAsset("../backend/lambda/lambda_auth"),
    handler: "lambda_function.lambda_handler",
    memorySize: 128,
    timeout: cdk.Duration.minutes(1),
    environment: {
      REGION_NAME: stack.regionName,
      USER_TABLE_NAME: stack.userInfoTable.tableName
    },
    role: lambdaRole
  });
  stack.lambdaAuth = lambdaAuth;


  if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => stack.deployType.includes(v))) {
    const lambdaQuery = new lambda.Function(stack, "Moderation-Lambda-Query", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_query"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      environment: {
        TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
        REGION_NAME: stack.regionName,
        TASK_ID_QUERY_INDEX: "TaskIdQueryIndex",
        TASK_ID_QUERY_INDEX_KEY_NAME: "task_id_query",
        USER_TABLE_NAME: stack.userInfoTable.tableName
      },
      role: lambdaRole
    });
    stack.lambdaQuery = lambdaQuery;

    const lambdaCallback = new lambda.Function(stack, "Moderation-Lambda-Callback", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_callback"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      environment: {
        REGION_NAME: stack.regionName,
        USER_TABLE_NAME: stack.userInfoTable.tableName
      },
      role: lambdaRole
    });
    stack.lambdaCallback = lambdaCallback;

    // Grant permissions for Lambda to read from the SQS queue
    stack.callbackQueue.grantConsumeMessages(lambdaCallback);

    // Add an event source for SQS to trigger Lambda
    lambdaCallback.addEventSource(
      new lambdaEventSources.SqsEventSource(stack.callbackQueue)
    );

    const lambdaSubmit = new lambda.Function(stack, "Moderation-Lambda-Submit", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_submit"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      role: lambdaRole
    });
    stack.lambdaSubmit = lambdaSubmit;

    const lambdaDaemon = new lambda.Function(stack, "Moderation-Lambda-Daemon", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_daemon"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      role: lambdaRole
    });
    stack.lambdaDaemon = lambdaDaemon;
  }

  const initialToken = uuid.v4();

  let tokenSecret = new secretsmanager.Secret(stack, `Moderation-TokenSecret`, {
    secretName: `${stack.stackName}-TokenSecretName`,
    secretStringValue: cdk.SecretValue.unsafePlainText(initialToken),
  });
  
  NagSuppressions.addResourceSuppressions(tokenSecret, [
    { id: 'AwsSolutions-SMG4', reason: 'This token is manually rotated and does not require automatic rotation.' }
  ], true);

  const lambdaInitDataInfo = new lambda.Function(stack, "Moderation-Lambda-InitInfo", {
    runtime: lambda.Runtime.PYTHON_3_12,
    code: lambda.Code.fromAsset("../backend/lambda/lambda_init_info"),
    handler: "lambda_function.lambda_handler",
    memorySize: 128,
    timeout: cdk.Duration.minutes(10),
    environment: {
      REGION_NAME: stack.regionName,
      USER_TABLE_NAME: stack.userInfoTable.tableName,
      USER_ID: stack.node.tryGetContext("user_id"),
      TOKEN_ARN: tokenSecret.secretArn,
      CALLBACK_URL: stack.node.tryGetContext("callback_url")
    },
    role: lambdaRole
  });
  tokenSecret.grantRead(lambdaInitDataInfo);


  new CfnOutput(stack, 'TestToken', {
        value: initialToken,
        description: 'TestToken'
  });


  stack.lambdaInitDataInfo = lambdaInitDataInfo;

  if ([TEXT_MODERATION].some(v => stack.deployType.includes(v))) {
    const lambdaTextModeration = new lambda.Function(stack, "Moderation-Lambda-Text-Moderation", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_text_moderation"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      environment: {
        REGION_NAME: stack.regionName,
        TAGS: stack.tagsJsonStr
      },
      role: lambdaRole
    });
    stack.lambdaTextModeration = lambdaTextModeration;

  }

  if ([IMAGE_MODERATION].some(v => stack.deployType.includes(v))) {    
    const lambdaImgModeration = new lambda.Function(stack, "Moderation-Lambda-Img-Moderation", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_img_moderation"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      environment: {
        REGION_NAME: stack.regionName,
        TAGS: stack.tagsJsonStr
      },
      role: lambdaRole
    });
    stack.lambdaImgModeration = lambdaImgModeration;
  }


  if ([AUDIO_MODERATION, VIDEO_MODERATION].some(v => stack.deployType.includes(v))) {
    const lambdaAudioVideoModerationFromS3 = new lambda.Function(stack, "Moderation-Lambda-Internal-TASK-FROM-S3", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../backend/lambda/lambda_audio_video_moderation_from_s3"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      role: lambdaRole
    });
    stack.lambdaAudioVideoModerationFromS3 = lambdaAudioVideoModerationFromS3;
  }
}


export function updateLambdaEnv(stack: BackendCdkStack): void {
  const commonEnvVars: { [key: string]: string } = {
    REGION_NAME: stack.regionName,
    PROGRAM_TYPE: "2",
    ATTEMPT_COUNT: "2",
    MODERATION_SQS: stack.moderationQueueUrl,
    CALLBACK_SQS: stack.callbackQueueUrl,
    TASK_TABLE_NAME: stack.taskTable.tableName,
    TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
    MODERATION_BUCKET_NAME: stack.s3BucketName,
    S3BUCKET_CUSTOMER_DIR: "moderation_results",
    WHISPER_ENDPOINT_NAME: stack.sagemakerEndpointName,
    SPEECH_RECOGNIZER_PLUGIN :'sagemaker',
    TEXT_MODERATION_PLUGIN: 'bedrock',
    VISUAL_MODERATION_TYPE :  stack.node.tryGetContext("visual_moderation_type"),
    IMAGE_MODERATION_PLUGIN :  stack.node.tryGetContext("image_moderation_plugin"),
    MODEL_ID:stack.node.tryGetContext("text_model_id"),
    IMG_MODEL_ID: stack.node.tryGetContext("img_model_id"),
    BATCH_PROCESS_IMG_NUMBER: "3",
    CLUSTER_NAME: stack.clusterName,
    S3_FILE_READABLE_EXPIRATION_TIME: stack.node.tryGetContext("file_expiration_time"),
    TASK_DEFINITION_ARN: stack.taskDefinitionArn,
    SUBNET_IDS: stack.privateSubnets.map(subnet => subnet.subnetId).join(','),
    CONTAINER_NAME: stack.containerName,
    SECURITY_GROUP_ID: stack.securityGroupId,
    TAGS: stack.tagsJsonStr
  };

  if ([AUDIO_MODERATION, VIDEO_MODERATION].some(v => stack.deployType.includes(v))) {
    commonEnvVars.S3_MODERATION_SQS = stack.s3ModerationQueueUrl;
  }

  function createLambdaEnvUpdate(idSuffix: string, lambdaFunction: lambda.Function, extraVars?: { [key: string]: string }) {
    const envVars = { ...commonEnvVars, ...extraVars };
    return new cr.AwsCustomResource(stack, `UpdateLambdaEnvironment${idSuffix}`, {
      onUpdate: {
        service: 'Lambda',
        action: 'updateFunctionConfiguration',
        parameters: {
          FunctionName: lambdaFunction.functionName,
          Environment: {
            Variables: envVars
          }
        },
        physicalResourceId: cr.PhysicalResourceId.of('LambdaEnvUpdate')
      },
      // policy: cr.AwsCustomResourcePolicy.fromStatements([
      //   new iam.PolicyStatement({
      //     actions: ['lambda:UpdateFunctionConfiguration'],
      //     resources: [lambdaFunction.functionArn]
      //   })
      // ]),
      role: stack.lambdaRole
    });
  }

  const submitExtraVars = { USER_TABLE_NAME: stack.userInfoTable.tableName };
  const updateLambdaEnv1 = createLambdaEnvUpdate("1", stack.lambdaSubmit, submitExtraVars);
  updateLambdaEnv1.node.addDependency(stack.lambdaSubmit);

  const updateLambdaEnv2 = createLambdaEnvUpdate("2", stack.lambdaDaemon);
  updateLambdaEnv2.node.addDependency(stack.lambdaDaemon);

  if ([AUDIO_MODERATION, VIDEO_MODERATION].some(v => stack.deployType.includes(v))) {
    const updateLambdaEnv3 = createLambdaEnvUpdate("3", stack.lambdaAudioVideoModerationFromS3);
    updateLambdaEnv3.node.addDependency(stack.lambdaAudioVideoModerationFromS3);
  }


}

export function initDataInfos(stack: BackendCdkStack): void {


  const initData = new cr.AwsCustomResource(stack, 'InvokeLambda', {
    onUpdate: {
      service: 'Lambda',
      action: 'invoke',
      parameters: {
        FunctionName: stack.lambdaInitDataInfo.functionName
      },
      physicalResourceId: cr.PhysicalResourceId.of('InvokeLambda')
    },
    policy: cr.AwsCustomResourcePolicy.fromStatements([
      new iam.PolicyStatement({
        actions: ['lambda:InvokeFunction'],
        resources: [stack.lambdaInitDataInfo.functionArn]
      })
    ]),
    role: stack.lambdaRole
  });

  initData.node.addDependency(stack.lambdaInitDataInfo);


}


