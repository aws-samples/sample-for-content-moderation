import * as cdk from 'aws-cdk-lib';
import { RemovalPolicy } from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { CfnOutput } from 'aws-cdk-lib';
import { AUDIO_MODERATION, VIDEO_MODERATION } from './config';
import { BackendCdkStack } from './backend_cdk_stack';
import { NagSuppressions } from 'cdk-nag';
import * as uuid from 'uuid';

export function createS3(stack: BackendCdkStack): void {

  // const bucket_name=`moderation-bucket-${uuid.v4().slice(0, 4)}`
  const bucket_name=`${stack.stackName }-bucket-${stack.regionName}`.toLowerCase()

  const bucket = new s3.Bucket(stack, 'Moderation-S3Bucket', {
    bucketName:bucket_name,
    publicReadAccess: false,
    enforceSSL: true,
    removalPolicy: RemovalPolicy.RETAIN,
    serverAccessLogsPrefix: 'access-logs/'
  });

  stack.s3BucketName =bucket_name;
  stack.s3Arn = `arn:aws:s3:::${bucket_name}`;
  stack.s3Bucket = bucket;


  new CfnOutput(stack, 'S3BucketName', {
    value: bucket.bucketName,
    description: 'S3 Bucket Name'
  });
}

export function setS3Event(stack: BackendCdkStack): void {

  if (stack.deployType.includes(AUDIO_MODERATION)) {
    stack.s3Bucket.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(stack.lambdaAudioVideoModerationFromS3),
      { prefix: 's3_audio_moderation/' }
    );
  }

  if (stack.deployType.includes(VIDEO_MODERATION)) {
    stack.s3Bucket?.addEventNotification(
      s3.EventType.OBJECT_CREATED,
      new s3n.LambdaDestination(stack.lambdaAudioVideoModerationFromS3),
      { prefix: 's3_video_moderation/' }
    );
  }
}
