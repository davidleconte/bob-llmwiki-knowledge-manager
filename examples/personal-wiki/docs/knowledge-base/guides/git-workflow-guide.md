# My Git Workflow

## Daily Workflow

### Starting Work
```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature
```

### Making Changes
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature
```

### Finishing Work
```bash
# Update from main
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main

# Push changes
git push origin feature/my-feature --force-with-lease

# Create pull request (via GitHub/GitLab)
```

## Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Tests
- chore: Maintenance

## Useful Commands

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Amend last commit
git commit --amend

# Interactive rebase
git rebase -i HEAD~3

# Stash changes
git stash
git stash pop

# Cherry-pick commit
git cherry-pick <commit-hash>
```

## Related Documents
- [CLI Commands](../references/cli-commands.md)
- [Vim Setup](./vim-setup-guide.md)
