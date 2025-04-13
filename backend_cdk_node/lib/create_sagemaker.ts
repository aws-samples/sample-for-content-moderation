import * as cdk from 'aws-cdk-lib';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as appscaling from 'aws-cdk-lib/aws-applicationautoscaling';
import { CfnOutput } from 'aws-cdk-lib';
import * as uuid from 'uuid';
import { BackendCdkStack } from './backend_cdk_stack';
import { NagSuppressions } from 'cdk-nag';

export function createSagemaker(stack: BackendCdkStack): void {


  // SageMaker permissions
  const modelName = `Moderation-Whisper-Model-${uuid.v4().slice(0, 8)}`;
  const endpointConfigName = `Moderation-Whisper-EndpointConfig-${uuid.v4().slice(0, 8)}`;
  const endpointName = `content-moderation-endpoint-whisper-v3-${uuid.v4().slice(0, 8)}`;


  
  const sagemakerRole = new iam.Role(stack, 'Moderation-SageMaker-Role', {
    assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
    managedPolicies: []
  });

 
    
  // 763104351884.dkr.ecr is the AWS public image library
  sagemakerRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      "ecr:GetAuthorizationToken",
      "ecr:ListTagsForResource",
      "ecr:ListImages",
      "ecr:DescribeRepositories",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetLifecyclePolicy",
      "ecr:DescribeImageScanFindings",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:DescribeImages",
      "ecr:GetRepositoryPolicy"
    ],
    resources: ["*"]
  }));

  NagSuppressions.addResourceSuppressions(sagemakerRole, [
    {
      id: 'AwsSolutions-IAM5',
      reason: 'SageMaker requires these permissions to access ECR ',
      appliesTo: ['Resource::*','Resource::arn:aws:sagemaker:us-west-2:*:model/*']
    }
  ], true);



  sagemakerRole.addToPolicy(new iam.PolicyStatement({
    actions: [
      'sagemaker:CreateModel',
      'sagemaker:DescribeModel',
      'sagemaker:CreateEndpointConfig',
      'sagemaker:CreateEndpoint',
      'sagemaker:DescribeEndpoint',
      'sagemaker:DescribeEndpointConfig',
      'sagemaker:InvokeEndpoint'
    ],
    resources: [
      `arn:aws:sagemaker:${stack.region}:${stack.account}:model/${modelName}`,
      `arn:aws:sagemaker:${stack.region}:${stack.account}:endpoint/${endpointName}`,
      `arn:aws:sagemaker:${stack.region}:${stack.account}:endpoint-config/${endpointConfigName}`
    ]
  }));




  const images = `763104351884.dkr.ecr.${stack.region}.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-gpu-py310-cu118-ubuntu20.04`;

  const model = new sagemaker.CfnModel(stack, 'Moderation-Whisper-Model', {
    modelName:modelName,
    executionRoleArn: sagemakerRole.roleArn,
    primaryContainer: {
      image: images,
      environment: {
        'HF_MODEL_ID': 'openai/whisper-large-v3-turbo',
        'HF_TASK': 'automatic-speech-recognition'
      }
    }
  });

  model.node.addDependency(sagemakerRole);


  const endpointConfig = new sagemaker.CfnEndpointConfig(stack, 'Moderation-Whisper-EndpointConfig', {
    endpointConfigName:endpointConfigName,
    productionVariants: [
      {
        initialInstanceCount: 1,
        instanceType: 'ml.g4dn.xlarge',
        modelName: modelName,
        variantName: 'AllTraffic',
        initialVariantWeight: 1.0
      }
    ]
  });

  endpointConfig.addDependency(model);


  const endpoint = new sagemaker.CfnEndpoint(stack, 'Moderation-Whisper-Endpoint', {
    endpointConfigName: endpointConfig.attrEndpointConfigName,
    endpointName: endpointName
  });

  endpoint.addDependency(endpointConfig);


  stack.sagemakerEndpointArn = cdk.Stack.of(stack).formatArn({
    service: 'sagemaker',
    resource: 'endpoint',
    resourceName: endpoint.endpointName
  });
  stack.sagemakerEndpointName = endpoint.endpointName;

  const scalingTarget = new appscaling.CfnScalableTarget(stack, 'Moderation-Whisper-ScalingTarget', {
    maxCapacity: 100,
    minCapacity: 1,
    resourceId: `endpoint/${endpoint.endpointName}/variant/AllTraffic`,
    roleArn: sagemakerRole.roleArn,
    scalableDimension: 'sagemaker:variant:DesiredInstanceCount',
    serviceNamespace: 'sagemaker'
  });

  scalingTarget.addDependency(endpoint);

  const scalingPolicy = new appscaling.CfnScalingPolicy(stack, 'Moderation-Whisper-ScalingPolicy', {
    policyName: 'SageMakerEndpointInvocationScalingPolicy',
    policyType: 'TargetTrackingScaling',
    scalableDimension: 'sagemaker:variant:DesiredInstanceCount',
    serviceNamespace: 'sagemaker',
    resourceId: `endpoint/${endpoint.endpointName}/variant/AllTraffic`,
    targetTrackingScalingPolicyConfiguration: {
      targetValue: 20.0,
      predefinedMetricSpecification: {
        predefinedMetricType: 'SageMakerVariantInvocationsPerInstance'
      },
      scaleInCooldown: 60,
      scaleOutCooldown: 60
    }
  });

  scalingPolicy.addDependency(scalingTarget);
  if (endpoint.endpointName) {
    new CfnOutput(stack, 'SageMakerEndpointName', {
      value: endpoint.endpointName,
      description: 'SageMaker Endpoint Name'
    });
  }
}
