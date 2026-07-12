# Docker Containers

## Overview
Docker containers are lightweight, standalone packages that include everything needed to run an application.

## Key Points
- Isolated from host system
- Portable across environments
- Efficient resource usage
- Fast startup times
- Immutable infrastructure

## Details

### Core Concepts

**Images:**
- Read-only templates
- Built from Dockerfile
- Layered filesystem
- Stored in registries

**Containers:**
- Running instances of images
- Writable layer on top
- Isolated processes
- Can be stopped/started

**Volumes:**
- Persistent data storage
- Shared between containers
- Survive container deletion

### Common Commands

```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -d -p 8080:80 myapp:latest

# List containers
docker ps

# Stop container
docker stop <container_id>

# Remove container
docker rm <container_id>
```

### Best Practices
- Use official base images
- Minimize layers
- Use .dockerignore
- Don't run as root
- Use multi-stage builds

## Related Documents
- [CLI Commands](../references/cli-commands.md)

## References
- [Docker Documentation](https://docs.docker.com/)
