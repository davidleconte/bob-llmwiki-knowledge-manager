# CLI Commands Reference

## Docker

```bash
# Build
docker build -t name:tag .

# Run
docker run -d -p 8080:80 name:tag

# Exec
docker exec -it container_id bash

# Logs
docker logs -f container_id

# Clean up
docker system prune -a
```

## Git

```bash
# Status
git status

# Add
git add .

# Commit
git commit -m "message"

# Push
git push origin branch

# Pull
git pull origin branch

# Branch
git branch -a
git checkout -b new-branch
```

## System

```bash
# Processes
ps aux | grep process
kill -9 PID

# Disk usage
df -h
du -sh directory

# Network
netstat -tuln
lsof -i :8080

# Find files
find . -name "*.py"
grep -r "pattern" .
```

## Package Management

```bash
# Homebrew (macOS)
brew install package
brew update
brew upgrade

# APT (Ubuntu)
sudo apt update
sudo apt install package
sudo apt upgrade
```

## Related Documents
- [Docker Containers](../concepts/docker-containers.md)
- [Git Workflow](../guides/git-workflow-guide.md)
