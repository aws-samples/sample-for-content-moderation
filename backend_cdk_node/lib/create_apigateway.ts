import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import { Duration } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import { Function as LambdaFunction } from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import { RemovalPolicy } from 'aws-cdk-lib';

import { AUDIO_MODERATION, IMAGE_MODERATION, LIVE_MODERATION, TEXT_MODERATION, VIDEO_MODERATION } from './config';
import { BackendCdkStack } from './backend_cdk_stack';
import { NagSuppressions } from 'cdk-nag';

export function createApiGateway(
  stack: BackendCdkStack
): apigateway.RestApi {


  const logGroup = new logs.LogGroup(stack, 'ApiGatewayLogs', {
    removalPolicy: RemovalPolicy.DESTROY
  });


  const api = new apigateway.RestApi(stack, 'Moderation-Api', {
    restApiName: 'Moderation API',
    description: 'This is a Moderation API',
    deployOptions: {
      stageName: 'api',
      loggingLevel: apigateway.MethodLoggingLevel.INFO,
      dataTraceEnabled: true,
      accessLogDestination: new apigateway.LogGroupLogDestination(logGroup),
      accessLogFormat: apigateway.AccessLogFormat.clf()
    },
    cloudWatchRole:true
  });

  const requestValidator = new apigateway.RequestValidator(stack, 'RequestValidator', {
    restApi: api,
    validateRequestBody: true,
    validateRequestParameters: true,
  });
  

  const authorizer = new apigateway.RequestAuthorizer(stack, 'ModerationApi-Authorizer', {
    handler: stack.lambdaAuth,
    identitySources: [
      apigateway.IdentitySource.header('token'),
      apigateway.IdentitySource.header('user_id')
    ],
    resultsCacheTtl: Duration.seconds(0)
  });

  if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => stack.deployType.includes(v as number))) {

    const queryModerationApi = api.root.addResource('query_moderation');
    const queryModerationIntegration = new apigateway.LambdaIntegration(stack.lambdaQuery);
    queryModerationApi.addMethod('POST', queryModerationIntegration, { authorizer,requestValidator });

    const submitModerationApi = api.root.addResource('submit_moderation');
    const submitModerationIntegration = new apigateway.LambdaIntegration(stack.lambdaSubmit);
    submitModerationApi.addMethod('POST', submitModerationIntegration, { authorizer,requestValidator });
  }

  if ([TEXT_MODERATION].some(v => stack.deployType.includes(v as number))) {

    const textModerationApi = api.root.addResource('text_moderation');
    const textModerationIntegration = new apigateway.LambdaIntegration(stack.lambdaTextModeration);
    textModerationApi.addMethod('POST', textModerationIntegration, { authorizer,requestValidator });
  }


  if ([IMAGE_MODERATION].some(v => stack.deployType.includes(v as number))) {

    const imgModerationApi = api.root.addResource('img_moderation');
    const imgModerationIntegration = new apigateway.LambdaIntegration(stack.lambdaImgModeration);
    imgModerationApi.addMethod('POST', imgModerationIntegration, { authorizer,requestValidator });
  }


  NagSuppressions.addResourceSuppressions(api, [
    {
      id: 'AwsSolutions-COG4',
      reason: 'Authentication is handled through other means'
    }
  ], true);

  NagSuppressions.addResourceSuppressions(api, [
    {
      id: 'AwsSolutions-IAM4',
      reason: 'Using the AWS-managed policy for API Gateway CloudWatch logging is acceptable here.'
    }
  ], true);

  return api;
}