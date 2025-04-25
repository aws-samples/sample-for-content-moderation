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
import { createLambdaRole } from './create_lambda_role';



export function createLambda(stack: BackendCdkStack): void {

  const lambdaRole = createLambdaRole(stack);


  const lambdaAuth = new lambda.Function(stack, "Moderation-Lambda-Auth", {
    runtime: lambda.Runtime.PYTHON_3_12,
    code: lambda.Code.fromAsset("../lambda/lambda_auth"),
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
      code: lambda.Code.fromAsset("../lambda/lambda_query"),
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
      code: lambda.Code.fromAsset("../lambda/lambda_callback"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(10),
      environment: {
        REGION_NAME: stack.regionName,
        USER_TABLE_NAME: stack.userInfoTable.tableName,
        TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
        TASK_TABLE_NAME: stack.taskTable.tableName
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
      code: lambda.Code.fromAsset("../lambda/lambda_submit"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      role: lambdaRole
    });
    stack.lambdaSubmit = lambdaSubmit;

    const lambdaDaemon = new lambda.Function(stack, "Moderation-Lambda-Daemon", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../lambda/lambda_daemon"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      role: lambdaRole
    });
    stack.lambdaDaemon = lambdaDaemon;


    const lambdaAudioInner = new lambda.Function(stack, "Moderation-Lambda-AudioInner", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../lambda/lambda_audio_moderation_inner"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      environment: {
        REGION_NAME: stack.regionName,
        MODERATION_BUCKET_NAME: stack.s3BucketName,
        TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
        CALLBACK_SQS: stack.callbackQueueUrl,
        S3_FILE_READABLE_EXPIRATION_TIME:  stack.node.tryGetContext("file_expiration_time"),
        WHISPER_ENDPOINT_NAME: stack.sagemakerEndpointName
      },
      role: lambdaRole
    });
    stack.lambdaAudioInner = lambdaAudioInner;

    // Grant permissions for Lambda to read from the SQS queue
    stack.moderationAudioQueue.grantConsumeMessages(lambdaAudioInner);


    // Add an event source for SQS to trigger Lambda
    lambdaAudioInner.addEventSource(
      new lambdaEventSources.SqsEventSource(stack.moderationAudioQueue)
    );



    const lambdaImgVideoInner = new lambda.Function(stack, "Moderation-Lambda-ImgVideoInner", {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../lambda/lambda_img_moderation_inner"),
      handler: "lambda_function.lambda_handler",
      memorySize: 128,
      timeout: cdk.Duration.minutes(15),
      environment: {
        REGION_NAME: stack.regionName,
        MODERATION_BUCKET_NAME: stack.s3BucketName,
        TASK_DETAIL_TABLE_NAME: stack.taskDetailTable.tableName,
        CALLBACK_SQS: stack.callbackQueueUrl,
        S3_FILE_READABLE_EXPIRATION_TIME:  stack.node.tryGetContext("file_expiration_time")
      },
      role: lambdaRole
    });
    stack.lambdaImgVideoInner = lambdaImgVideoInner;

    // Grant permissions for Lambda to read from the SQS queue
    stack.moderationVideoQueue.grantConsumeMessages(lambdaImgVideoInner);
    stack.moderationImgQueue.grantConsumeMessages(lambdaImgVideoInner);


    // Add an event source for SQS to trigger Lambda
    lambdaImgVideoInner.addEventSource(
      new lambdaEventSources.SqsEventSource(stack.moderationVideoQueue)
    );
    lambdaImgVideoInner.addEventSource(
      new lambdaEventSources.SqsEventSource(stack.moderationImgQueue)
    );
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
    code: lambda.Code.fromAsset("../lambda/lambda_init_info"),
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
      code: lambda.Code.fromAsset("../lambda/lambda_text_moderation"),
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
      code: lambda.Code.fromAsset("../lambda/lambda_img_moderation"),
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
      code: lambda.Code.fromAsset("../lambda/lambda_audio_video_moderation_from_s3"),
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
    ATTEMPT_COUNT: "3",

    MODERATION_SQS: stack.moderationQueueUrl,
    CALLBACK_SQS: stack.callbackQueueUrl,


    IMAGE_MODERATION_SQS: stack.moderationImgQueueUrl,
    AUDIO_MODERATION_SQS: stack.moderationAudioQueueUrl,
    VIDEO_MODERATION_SQS: stack.moderationVideoQueueUrl,

    TASK_TABLE_NAME: stack.taskTable.tableName,
    MODERATION_BUCKET_NAME: stack.s3BucketName,
    S3BUCKET_CUSTOMER_DIR: "moderation_results",
    WHISPER_ENDPOINT_NAME: stack.sagemakerEndpointName,


    VISUAL_MODERATION_TYPE :  stack.node.tryGetContext("visual_moderation_type"),

    TEXT_MODEL_ID:stack.node.tryGetContext("text_model_id"),
    IMG_MODEL_ID: stack.node.tryGetContext("img_model_id"),
    VIDEO_MODEL_ID: stack.node.tryGetContext("video_model_id"),


    CLUSTER_NAME: stack.clusterName,
    S3_FILE_READABLE_EXPIRATION_TIME: stack.node.tryGetContext("file_expiration_time"),
    TASK_DEFINITION_ARN: stack.taskDefinitionArn,
    SUBNET_IDS: stack.subnets.map(subnet => subnet.subnetId).join(','),
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
