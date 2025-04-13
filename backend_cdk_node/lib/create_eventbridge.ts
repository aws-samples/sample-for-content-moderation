import * as cdk from 'aws-cdk-lib';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Duration } from 'aws-cdk-lib';
import { BackendCdkStack } from './backend_cdk_stack';

export function createEventbridge(stack: BackendCdkStack): void {
  const rule = new events.Rule(stack, 'Moderation-ScheduleRule', {
    schedule: events.Schedule.rate(Duration.minutes(2)),
    targets: [new targets.LambdaFunction(stack.lambdaDaemon)]
  });
}
