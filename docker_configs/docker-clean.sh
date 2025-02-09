#!/usr/bin/env bash

# Remove unused images
echo "Remove unused images..."
docker image prune -a 

# Remove stopped containers
echo "Remove stopped containers..."
docker container prune 

# Remove unused volumes
echo "Remove unused volumes..."
docker volume prune 

# Remove unused networks
echo "Remove unused networks..."
docker network prune 

# Remove all unused resources (images, containers, volumes, networks)
echo "Remove all unused resources..."
docker system prune -a --volumes 

# Remove build cache
echo "Remove build cache..."
docker builder prune 