#!/bin/bash
ACCOUNT="292075781285"
DOCKER_CONTAINER="rob-ometif-2-zarr"
REPO=${ACCOUNT}.dkr.ecr.us-east-1.amazonaws.com/${DOCKER_CONTAINER}
TAG=build-$(date -u "+%Y-%m-%d")
echo "Building Docker Image..."
docker build -t $DOCKER_CONTAINER .
echo "Authenticating against AWS ECR..."
# eval $(aws ecr get-login --no-include-email --region us-east-1)
eval $(aws ecr get-login --no-include-email --region us-east-1)
# eval $(aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 292075781285.dkr.ecr.us-east-1.amazonaws.com)
echo "Tagging ${REPO}..."
echo "docker tag $DOCKER_CONTAINER:latest $REPO:$TAG"

docker tag $DOCKER_CONTAINER:latest $REPO:$TAG
docker tag $DOCKER_CONTAINER:latest $REPO:latest
echo "Deploying to AWS ECR"
docker push $REPO