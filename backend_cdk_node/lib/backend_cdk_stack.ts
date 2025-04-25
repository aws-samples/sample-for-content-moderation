import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Tags } from 'aws-cdk-lib';
import { createApiGateway } from './create_apigateway';
import { createDDB } from './create_ddb';
import { createEcs } from './create_ecs';
import { createEventbridge } from './create_eventbridge';
import { createLambda,updateLambdaEnv,initDataInfos } from './create_lambda';
import { createS3, setS3Event } from './create_s3';
import { createSagemaker } from './create_sagemaker';
import { createSqs } from './create_sqs';
import { TEXT_MODERATION, IMAGE_MODERATION, AUDIO_MODERATION, VIDEO_MODERATION, LIVE_MODERATION } from './config';

export class BackendCdkStack extends cdk.Stack {
    regionName: string;
    accountId: string;
    repositoryName: string;
    deployType: number[];
    r_tags: any [];
    tagsJsonStr:string;

    moderationImgQueue:any;
    moderationImgQueueUrl:string;
    moderationImgQueueArn:string;

    moderationVideoQueue:any;
    moderationVideoQueueUrl:string;
    moderationVideoQueueArn:string;

    moderationAudioQueue:any;
    moderationAudioQueueUrl:string;
    moderationAudioQueueArn:string;

    callbackQueueUrl:string;
    callbackQueueArn:string;
    s3ModerationQueueUrl:string;
    s3ModerationQueueArn:string;
    moderationQueueUrl:string;
    moderationQueueArn:string;

    s3Arn:string;
    s3Bucket:any;
    s3BucketName:string;

    lambdaAudioVideoModerationFromS3:any;
    sagemakerEndpointArn:string;
    sagemakerEndpointName:any;

    ecsArn:string;


    taskTable:any;
    taskDetailTable:any;
    userInfoTable:any;

    lambdaAuth:any;
    lambdaRole:any;
    lambdaQuery:any;
    lambdaCallback:any;
    callbackQueue:any;
    lambdaSubmit:any;
    lambdaDaemon:any;
    lambdaInitDataInfo:any;
    lambdaTextModeration:any;
    lambdaImgModeration:any;

    lambdaImgVideoInner:any;
    lambdaAudioInner:any;

    taskRole:any;
    taskExecutionRole:any;
    clusterName:string;
    taskDefinitionArn:string;
    subnets:any [];
    containerName:string;
    securityGroup:string;
    securityGroupId:string;

    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        this.initTags();

        this.regionName = cdk.Stack.of(this).region;
        this.accountId = cdk.Stack.of(this).account;
        this.repositoryName = this.node.tryGetContext("repository_name");
        this.deployType = this.node.tryGetContext("deploy_type");

        // There are dependencies between components, please do not change the order of creation
        // 组件之间有依赖关系，请勿修改创建的顺序
        createDDB(this);

        if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => this.deployType.includes(v as number))) {
            createSqs(this);
        }

        createS3(this);

        if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => this.deployType.includes(v as number))) {
            createSagemaker(this);
            // createEventbridge(this)
            createEcs(this);
        }

        createLambda(this);

        setS3Event(this);
        createApiGateway(this);

        if ([VIDEO_MODERATION, AUDIO_MODERATION, LIVE_MODERATION].some(v => this.deployType.includes(v))) {
            updateLambdaEnv(this);
        }

        initDataInfos(this);
    }

    private initTags(): void {
        this.r_tags = [
            { key: 'Environment', value: 'Dev' },
            { key: 'Project', value: 'Moderation' }
        ];

        this.r_tags.forEach(tag => Tags.of(this).add(tag.key, tag.value));
        this.tagsJsonStr = JSON.stringify(this.r_tags);
    }
}
