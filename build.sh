#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <root_directory> <docker_namespace>"
    exit 1
fi

docker_namespace=$2
root_directory=$1

base_image="${docker_namespace}/swe-bench"

# First, build the base image
echo "Building base Docker image..."
docker build -t "${base_image}-base:latest" -f "$root_directory/base/Dockerfile" .

build_docker_images() {
    # Build images in the root level directories first (except 'base' which is already built)
    for dir in $root_directory/*/; do
        if [[ "$dir" != *"/base/" ]]; then
            dockerfile_path="$dir/Dockerfile"
            if [ -f "$dockerfile_path" ]; then
                tag="${dir#$root_directory/}"
                tag="${tag%/}"
                image_name="$base_image-${tag//\//__}"
                echo "Building Docker image: $image_name"
                docker build -t "$image_name:latest" -f "$dockerfile_path" .
            fi
        fi
    done

    # Then build images in the versioned subdirectories
    for dir in $root_directory/*/*; do
        if [ -d "$dir" ] && [[ "$dir" =~ .*/[0-9]+\.[0-9]+$ ]]; then
            dockerfile_path="$dir/Dockerfile"
            if [ -f "$dockerfile_path" ]; then
                base_dir=$(dirname "$dir")
                version=$(basename "$dir")
                tag_base="${base_dir#$root_directory/}"
                tag_base="${tag_base//\//__}"
                image_name="$base_image-${tag_base}-testbed"
                echo "Building Docker image: $image_name:$version for $dir/Dockerfile"
                docker build -t "$image_name:$version" -f "$dockerfile_path" .
            fi
        fi
    done
}

build_docker_images
