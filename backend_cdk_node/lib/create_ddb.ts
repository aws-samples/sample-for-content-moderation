import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';
import { CfnOutput, RemovalPolicy } from 'aws-cdk-lib';
import { AUDIO_MODERATION, IMAGE_MODERATION, LIVE_MODERATION, TEXT_MODERATION, VIDEO_MODERATION } from './config';
import { BackendCdkStack } from './backend_cdk_stack';

export function createDDB(stack: BackendCdkStack) {
  let taskTable: dynamodb.Table | undefined;
  let taskDetailTable: dynamodb.Table | undefined;
  let userInfoTable: dynamodb.Table;

  if (stack.deployType.some(v => [VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].includes(v as number))) {
    taskTable = new dynamodb.Table(stack, 'Moderation-TaskTable', {
      partitionKey: { name: 'task_id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY
    });

    taskTable.addGlobalSecondaryIndex({
      indexName: 'UserIdIndex',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'create_time', type: dynamodb.AttributeType.STRING }
    });

    taskDetailTable = new dynamodb.Table(stack, 'Moderation-TaskDetailTable', {
      partitionKey: { name: 'task_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY
    });

    taskDetailTable.addGlobalSecondaryIndex({
      indexName: 'TaskIdQueryIndex',
      partitionKey: { name: 'task_id_query', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER }
    });
  }

  userInfoTable = new dynamodb.Table(stack, 'Moderation-UserInfoTable', {
    partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
    billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
    removalPolicy: RemovalPolicy.DESTROY
  });

  if (stack.deployType.some(v => [VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].includes(v as number))) {
    new CfnOutput(stack, 'TASK_TABLE_NAME', {
      value: taskTable!.tableName,
      description: 'Task table name'
    });

    new CfnOutput(stack, 'TASK_DETAIL_TABLE_NAME', {
      value: taskDetailTable!.tableName,
      description: 'Task detail table name'
    });
  }

  stack.taskTable=taskTable
  stack.taskDetailTable=taskDetailTable
  stack.userInfoTable=userInfoTable
  

}