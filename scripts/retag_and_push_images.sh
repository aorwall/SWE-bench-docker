#!/bin/bash
# This script is used to retag and push Docker images from one namespace to another
# Usage: ./retag_and_push_images.sh <source_namespace> <target_namespace>
# Example: ./retag_and_push_images.sh aorwall xingyaoww

SOURCE_NAME=$1
TARGET_NAME=$2

# Loop through all Docker images starting with 'aorwall'
docker images --format '{{.Repository}}:{{.Tag}}' | grep '^'${SOURCE_NAME}'/' | while read -r image; do
    # Replace 'aorwall' with 'xingyaoww' in the repository name
    new_image="${image/${SOURCE_NAME}/${TARGET_NAME}}"
    
    # Docker tag command to retag the image
    echo "Retagging $image to $new_image"
    docker tag "$image" "$new_image"
    
    echo "Retagged $image to $new_image"
    
    docker push "$new_image"
done
