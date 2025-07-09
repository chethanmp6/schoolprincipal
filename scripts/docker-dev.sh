#!/bin/bash
# Development Docker helper script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 SchoolBot Docker Development Helper${NC}"
echo -e "${BLUE}======================================${NC}"

# Function to display usage
usage() {
    echo -e "${YELLOW}Usage: $0 {build|up|down|logs|shell|clean|rebuild}${NC}"
    echo ""
    echo "Commands:"
    echo "  build    - Build the Docker image"
    echo "  up       - Start the application with Docker Compose"
    echo "  down     - Stop the application"
    echo "  logs     - Show application logs"
    echo "  shell    - Open a shell in the running container"
    echo "  clean    - Remove all containers and images"
    echo "  rebuild  - Clean build and start"
    echo ""
    exit 1
}

# Function to build the image
build() {
    echo -e "${GREEN}🔨 Building SchoolBot Docker image...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Build completed!${NC}"
}

# Function to start the application
up() {
    echo -e "${GREEN}🚀 Starting SchoolBot application...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Application started!${NC}"
    echo -e "${YELLOW}📡 Access the application at: http://localhost:8000${NC}"
    echo -e "${YELLOW}📚 API documentation at: http://localhost:8000/docs${NC}"
}

# Function to stop the application
down() {
    echo -e "${YELLOW}🛑 Stopping SchoolBot application...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Application stopped!${NC}"
}

# Function to show logs
logs() {
    echo -e "${BLUE}📋 Showing application logs...${NC}"
    docker-compose logs -f
}

# Function to open a shell
shell() {
    echo -e "${BLUE}🐚 Opening shell in SchoolBot container...${NC}"
    docker-compose exec schoolbot /bin/bash
}

# Function to clean everything
clean() {
    echo -e "${RED}🧹 Cleaning Docker containers and images...${NC}"
    docker-compose down -v
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
}

# Function to rebuild everything
rebuild() {
    echo -e "${YELLOW}🔄 Rebuilding SchoolBot application...${NC}"
    down
    clean
    build
    up
    echo -e "${GREEN}✅ Rebuild completed!${NC}"
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    up)
        up
        ;;
    down)
        down
        ;;
    logs)
        logs
        ;;
    shell)
        shell
        ;;
    clean)
        clean
        ;;
    rebuild)
        rebuild
        ;;
    *)
        usage
        ;;
esac