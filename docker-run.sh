#!/bin/bash

# Docker run script for BC TA System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}BC TA System Docker Setup${NC}"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  run         Run the container"
    echo "  dev         Run in development mode with docker-compose"
    echo "  prod        Build and run production image"
    echo "  stop        Stop all containers"
    echo "  clean       Clean up containers and images"
    echo "  logs        Show container logs"
    echo ""
}

# Build Docker image
build_image() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t bc-tasystem:latest .
    echo -e "${GREEN}Build completed!${NC}"
}

# Run Docker container
run_container() {
    echo -e "${YELLOW}Running container...${NC}"
    docker run -d \
        --name bc-tasystem \
        -p 8080:8080 \
        -e DEBUG=True \
        bc-tasystem:latest
    echo -e "${GREEN}Container started! Access the application at http://localhost:8080${NC}"
}

# Run in development mode
run_dev() {
    echo -e "${YELLOW}Starting development environment...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Development environment started! Access the application at http://localhost:8080${NC}"
}

# Build and run production
run_prod() {
    echo -e "${YELLOW}Building production image...${NC}"
    docker build -f Dockerfile.prod -t bc-tasystem:prod .
    echo -e "${YELLOW}Running production container...${NC}"
    docker run -d \
        --name bc-tasystem-prod \
        -p 8080:8080 \
        -e DEBUG=False \
        bc-tasystem:prod
    echo -e "${GREEN}Production container started! Access the application at http://localhost:8080${NC}"
}

# Stop containers
stop_containers() {
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose down 2>/dev/null || true
    docker stop bc-tasystem bc-tasystem-prod 2>/dev/null || true
    docker rm bc-tasystem bc-tasystem-prod 2>/dev/null || true
    echo -e "${GREEN}Containers stopped!${NC}"
}

# Clean up
clean_up() {
    echo -e "${YELLOW}Cleaning up containers and images...${NC}"
    docker-compose down -v 2>/dev/null || true
    docker stop bc-tasystem bc-tasystem-prod 2>/dev/null || true
    docker rm bc-tasystem bc-tasystem-prod 2>/dev/null || true
    docker rmi bc-tasystem:latest bc-tasystem:prod 2>/dev/null || true
    echo -e "${GREEN}Cleanup completed!${NC}"
}

# Show logs
show_logs() {
    echo -e "${YELLOW}Showing container logs...${NC}"
    docker logs -f bc-tasystem 2>/dev/null || docker logs -f bc-tasystem-prod 2>/dev/null || echo "No containers running"
}

# Main script logic
case "${1:-}" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    dev)
        run_dev
        ;;
    prod)
        run_prod
        ;;
    stop)
        stop_containers
        ;;
    clean)
        clean_up
        ;;
    logs)
        show_logs
        ;;
    *)
        show_usage
        ;;
esac
