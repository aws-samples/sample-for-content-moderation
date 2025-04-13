#!/bin/bash

# Check if all required arguments are provided
if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <aws-account-id> <region> <repository-name> <dockerfile-path>"
    echo "Example: bash ecr.sh xxxxxxxx us-west-2 moderation_repository ../backend/"

    exit 1
fi

# Assign arguments to variables
ACCOUNT_ID="$1"
REGION="$2"
REPO_NAME="$3"
DOCKERFILE_PATH="$4"


# Install dependencies required by some libraries
# pip install -r ../backend/lambda/lambda_callback/requirements.txt --target ../backend/lambda/lambda_callback/lib


# Create ECR repository
echo "Creating ECR repository..."
aws ecr create-repository --repository-name "$REPO_NAME" --region "$REGION" &>/dev/null

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# Build Docker image
echo "Building Docker image..."
docker build -t "$REPO_NAME:v01" "$DOCKERFILE_PATH"
#docker buildx build --platform linux/arm64 -t "$REPO_NAME:v01" "$DOCKERFILE_PATH" --push

# Tag Docker image
echo "Tagging Docker image..."
docker tag "$REPO_NAME:v01" "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:v01"

# Push Docker image to ECR
echo "Pushing Docker image to ECR..."
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:v01"

echo "Process completed successfully!"