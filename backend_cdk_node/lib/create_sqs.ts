import * as cdk from 'aws-cdk-lib';
import { Duration } from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as iam from 'aws-cdk-lib/aws-iam'; 

import { AUDIO_MODERATION, LIVE_MODERATION, VIDEO_MODERATION } from './config';
import { BackendCdkStack } from './backend_cdk_stack';

function createSecureQueue(stack: cdk.Stack, id: string, props?: sqs.QueueProps): sqs.Queue {
  const queue = new sqs.Queue(stack, id, {
    encryption: sqs.QueueEncryption.SQS_MANAGED,
    enforceSSL: true,
    ...props,
  });

  queue.addToResourcePolicy(new iam.PolicyStatement({
    effect: iam.Effect.DENY,
    principals: [new iam.AnyPrincipal()],
    actions: ['sqs:*'],
    resources: [queue.queueArn],
    conditions: {
      'Bool': {
        'aws:SecureTransport': 'false'
      }
    }
  }));

  return queue;
}

export function createSqs(stack: BackendCdkStack): void {
  // Create content moderation SQS queue
  const moderationQueueDlp = createSecureQueue(stack, 'Moderation-SQS-Moderation-DLQ', {
    visibilityTimeout: Duration.hours(12),
  });

  const moderationQueue = createSecureQueue(stack, 'Moderation-SQS-Moderation', {
    visibilityTimeout: Duration.hours(12),
    deadLetterQueue: {
      maxReceiveCount: 3,
      queue: moderationQueueDlp,
    },
  });

  stack.moderationQueueUrl = moderationQueue.queueUrl;
  stack.moderationQueueArn = moderationQueue.queueArn;

  // Create internal content moderation SQS queue from S3
  if ([VIDEO_MODERATION, AUDIO_MODERATION].some(v => stack.deployType.includes(v as number))) {
    const s3ModerationQueueDlp = createSecureQueue(stack, 'Moderation-SQS-S3-Moderation-DLQ', {
      visibilityTimeout: Duration.hours(12),
    });

    const s3ModerationQueue = createSecureQueue(stack, 'Moderation-SQS-S3-Moderation', {
      visibilityTimeout: Duration.hours(12),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: s3ModerationQueueDlp,
      },
    });

    stack.s3ModerationQueueUrl = s3ModerationQueue.queueUrl;
    stack.s3ModerationQueueArn = s3ModerationQueue.queueArn;
  }

  // Create callback SQS queue
  const callbackQueueDlp = createSecureQueue(stack, 'Moderation-SQS-Callback-DLQ', {
    visibilityTimeout: Duration.minutes(30),
    
  });

  const callbackQueue = createSecureQueue(stack, 'Moderation-SQS-Callback', {
    visibilityTimeout: Duration.minutes(30),
    deadLetterQueue: {
      maxReceiveCount: 3,
      queue: callbackQueueDlp,
    },
  });
  stack.callbackQueue = callbackQueue;
  stack.callbackQueueUrl = callbackQueue.queueUrl;
  stack.callbackQueueArn  = callbackQueue.queueArn;






  if ([LIVE_MODERATION].some(v => stack.deployType.includes(v as number))) {
    // Create content moderation SQS queue  inter
    const moderationImgQueueDlq = createSecureQueue(stack, 'Moderation-SQS-Moderation-IMG-DLQ', {
      visibilityTimeout: Duration.hours(12),
    });

    const moderationImgQueue = createSecureQueue(stack, 'Moderation-SQS-Moderation-IMG', {
      visibilityTimeout: Duration.hours(12),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: moderationImgQueueDlq,
      },
    });

    stack.moderationImgQueue = moderationImgQueue;
    stack.moderationImgQueueUrl = moderationImgQueue.queueUrl;
    stack.moderationImgQueueArn = moderationImgQueue.queueArn;


    const moderationVideoQueueDlq = createSecureQueue(stack, 'Moderation-SQS-Moderation-Video-DLQ', {
      visibilityTimeout: Duration.hours(12),
    });

    const moderationVideoQueue = createSecureQueue(stack, 'Moderation-SQS-Moderation-Video', {
      visibilityTimeout: Duration.hours(12),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: moderationVideoQueueDlq,
      },
    });
    stack.moderationVideoQueue = moderationVideoQueue;
    stack.moderationVideoQueueUrl = moderationVideoQueue.queueUrl;
    stack.moderationVideoQueueArn = moderationVideoQueue.queueArn;


    const moderationAudioQueueDlq = createSecureQueue(stack, 'Moderation-SQS-Moderation-Audio-DLQ', {
      visibilityTimeout: Duration.hours(12),
    });

    const moderationAudioQueue = createSecureQueue(stack, 'Moderation-SQS-Moderation-Audio', {
      visibilityTimeout: Duration.hours(12),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: moderationAudioQueueDlq,
      },
    });

    stack.moderationAudioQueue = moderationAudioQueue;
    stack.moderationAudioQueueUrl = moderationAudioQueue.queueUrl;
    stack.moderationAudioQueueArn = moderationAudioQueue.queueArn;

  }
}