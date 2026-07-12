# Installation Guide

This guide covers installing Bob Shell Knowledge Manager on your system.

## Prerequisites

- **Bob Shell** version 1.0.0 or higher
- **Git** (optional, for cloning the repository)
- **Operating System**: macOS, Linux, or Windows with WSL

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

```bash
# Clone the repository
cd ~/Projects
git clone https://github.com/yourusername/bob-llmwiki-knowledge-manager.git
cd bob-llmwiki-knowledge-manager

# Run installation script
./scripts/install.sh
```

### Method 2: Download ZIP

1. Download the latest release from GitHub
2. Extract to `~/Projects/bob-llmwiki-knowledge-manager`
3. Run the installation script:

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/install.sh
```

## What Gets Installed

The installation script will:

1. **Detect Bob Shell Configuration**
   - Looks for `~/.bob/` or `~/.config/bob/`
   - Exits with error if Bob Shell is not found

2. **Install Custom Mode**
   - Copies `config/custom_modes.yaml` to Bob Shell config directory
   - Backs up existing `custom_modes.yaml` if present
   - Creates `custom_modes.yaml.backup`

3. **Install Settings (Optional)**
   - Copies `config/settings.json` if it doesn't exist
   - Skips if `settings.json` already exists (won't overwrite)

## Verification

Verify the installation was successful:

```bash
# Check if the mode file exists
ls -la ~/.bob/custom_modes.yaml

# Start Bob Shell and check available modes
bob
/mode knowledge-manager
```

You should see the knowledge-manager mode available.

## Troubleshooting

### Bob Shell Not Found

**Error**: `Bob Shell config directory not found`

**Solution**: Ensure Bob Shell is installed and has been run at least once to create its configuration directory.

### Permission Denied

**Error**: `Permission denied` when running scripts

**Solution**: Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Existing Configuration

**Warning**: `custom_modes.yaml already exists`

The installer automatically backs up your existing configuration to `custom_modes.yaml.backup`. Your previous modes are preserved.

To merge configurations manually:

```bash
# View the backup
cat ~/.bob/custom_modes.yaml.backup

# Edit the new configuration
nano ~/.bob/custom_modes.yaml
```

## Uninstallation

To remove Bob Shell Knowledge Manager:

```bash
# Remove the custom mode
rm ~/.bob/custom_modes.yaml

# Restore backup if you had previous modes
mv ~/.bob/custom_modes.yaml.backup ~/.bob/custom_modes.yaml

# Remove the project directory
rm -rf ~/Projects/bob-llmwiki-knowledge-manager
```

## Next Steps

After installation:

1. **Initialize a Knowledge Base**: See [Usage Guide](USAGE.md#initialization)
2. **Start Using**: See [Usage Guide](USAGE.md#basic-usage)
3. **Customize**: See [Customization Guide](CUSTOMIZATION.md)

## System Requirements

### Minimum Requirements

- **Disk Space**: ~5 MB for the project
- **Memory**: No additional requirements (uses Bob Shell)
- **CPU**: No additional requirements

### Optional Dependencies

For export functionality:

- **Pandoc**: Required for HTML and PDF export
  ```bash
  # macOS
  brew install pandoc
  
  # Ubuntu/Debian
  sudo apt-get install pandoc
  
  # Fedora
  sudo dnf install pandoc
  ```

## Multiple Projects

You can use the same installation across multiple projects:

```bash
# Install once
cd ~/Projects/bob-llmwiki-knowledge-manager
./scripts/install.sh

# Initialize in any project
cd ~/Projects/project-1
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh

cd ~/Projects/project-2
~/Projects/bob-llmwiki-knowledge-manager/scripts/init-project.sh
```

Each project gets its own independent knowledge base.

## Updating

To update to a new version:

```bash
cd ~/Projects/bob-llmwiki-knowledge-manager

# Pull latest changes
git pull origin main

# Reinstall (backs up existing config)
./scripts/install.sh
```

Your knowledge bases in individual projects are not affected by updates.

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [GitHub Issues](https://github.com/yourusername/bob-llmwiki-knowledge-manager/issues)
3. Create a new issue with:
   - Your operating system
   - Bob Shell version
   - Error messages
   - Steps to reproduce
