#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BackendCdkStack } from '../lib/backend_cdk_stack';
import { AwsSolutionsChecks } from 'cdk-nag'
import { Aspects } from 'aws-cdk-lib';

const app = new cdk.App();


const accountId = app.node.tryGetContext("account_id");
const regionName = app.node.tryGetContext("region_name");


// Aspects.of(app).add(new AwsSolutionsChecks({ verbose: true }))

new BackendCdkStack(app, `Moderaion-${accountId.slice(0, 8)}-031`, {
    env: { account: accountId, region: regionName },
});

