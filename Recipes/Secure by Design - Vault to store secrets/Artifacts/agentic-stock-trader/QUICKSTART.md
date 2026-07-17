# Agentic Stock Trader - Quick Start Guide

This guide will help you quickly get the demo application running for your Vault demonstration.

## Prerequisites

✅ Java 11+ installed  
✅ Maven 3.6+ installed  
✅ Podman installed and running  
✅ HashiCorp Vault (for the actual demo)

## Quick Start (5 minutes)

### 1. Navigate to the Project

```bash
cd agentic-stock-trader
```

### 2. Create Backup (IMPORTANT - Do This First!)

Before making any changes, create a backup of the exposed secrets version:

```bash
./reset-to-exposed-secrets.sh backup
```

### 3. Build the Container

```bash
./build.sh
```

This will:
- Compile the Java application
- Package it as a JAR
- Build a container image

### 4. Run the Application

```bash
./run.sh
```

You'll see output showing **ALL THE EXPOSED SECRETS** including:
- API Keys (Alpha Vantage, Finnhub, Polygon, Trading API)
- Database credentials (username/password)
- AWS credentials (Access Key ID, Secret Access Key)

## Demo Workflow

### Phase 1: Show the Problem

1. **Run the application** - Point out all the secrets in the console output
2. **Show the source code** - Open `src/main/java/com/demo/stocktrader/AgenticStockTrader.java`
3. **Highlight the hardcoded secrets** - Lines 11-24 contain all the exposed credentials

### Phase 2: Vault Integration

Now demonstrate how to secure these secrets with Vault:

#### Step 1: Start Vault (if not already running)

```bash
vault server -dev
```

In another terminal, set the Vault address:

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
```

#### Step 2: Store Secrets in Vault

```bash
# API Keys
vault kv put secret/stocktrader/api \
  alpha_vantage_key="AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP" \
  finnhub_key="c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8" \
  polygon_key="PKG_demo_key_987654321_ABCDEFGH" \
  trading_secret="sk_live_51HyperSecretTradingKey789XYZ"

# Database Credentials
vault kv put secret/stocktrader/database \
  host="localhost" \
  port="5432" \
  name="stocktrader_db" \
  username="admin" \
  password="SuperSecret123!@#"

# AWS Credentials
vault kv put secret/stocktrader/aws \
  access_key_id="AKIAIOSFODNN7EXAMPLE" \
  secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

#### Step 3: Verify Secrets are Stored

```bash
vault kv get secret/stocktrader/api
vault kv get secret/stocktrader/database
vault kv get secret/stocktrader/aws
```

#### Step 4: Modify the Code

Now you would modify `AgenticStockTrader.java` to:
1. Add Vault client dependency to `pom.xml`
2. Replace hardcoded secrets with Vault API calls
3. Retrieve secrets from Vault at runtime

Example code change (conceptual):

```java
// Instead of:
private static final String ALPHA_VANTAGE_API_KEY = "AV_DEMO_KEY_12345...";

// Use:
private String getSecretFromVault(String path, String key) {
    // Vault client code here
    return vaultClient.read(path).getData().get(key);
}
```

#### Step 5: Rebuild and Test

```bash
./build.sh
./run.sh
```

Now the secrets are retrieved from Vault instead of being hardcoded!

### Phase 3: Reset for Next Demo

After your demonstration, restore the original exposed secrets version:

```bash
./reset-to-exposed-secrets.sh restore
./build.sh
```

The application is now back to its original state with exposed secrets, ready for the next demo!

## Exposed Secrets Reference

For your demo, here are all the secrets that are intentionally exposed:

### API Keys
- **Alpha Vantage**: `AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP`
- **Finnhub**: `c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8`
- **Polygon**: `PKG_demo_key_987654321_ABCDEFGH`
- **Trading API**: `sk_live_51HyperSecretTradingKey789XYZ`

### Database Credentials
- **Host**: `localhost:5432`
- **Database**: `stocktrader_db`
- **Username**: `admin`
- **Password**: `SuperSecret123!@#`

### AWS Credentials
- **Access Key ID**: `AKIAIOSFODNN7EXAMPLE`
- **Secret Access Key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

## Reset Script Commands

```bash
# Create backup (do this FIRST!)
./reset-to-exposed-secrets.sh backup

# Check current status
./reset-to-exposed-secrets.sh status

# Restore exposed secrets version
./reset-to-exposed-secrets.sh restore
```

## Troubleshooting

### Podman not running
```bash
podman machine start
```

### Build fails
- Ensure Java 11+ and Maven are installed
- Check you're in the `agentic-stock-trader` directory

### Scripts not executable
```bash
chmod +x build.sh run.sh reset-to-exposed-secrets.sh
```

### Need to see the backup file
```bash
ls -la *.exposed-secrets
```

## Demo Tips

1. **Start with the backup** - Always run `./reset-to-exposed-secrets.sh backup` before your first demo
2. **Show the output first** - Run the app and let people see all the secrets in the console
3. **Then show the code** - Open the Java file and point to the hardcoded values
4. **Emphasize the problem** - These secrets are in version control, logs, and memory dumps
5. **Show Vault as the solution** - Store secrets securely, rotate them, audit access
6. **Reset between demos** - Use the restore command to quickly reset for the next audience

## What the Application Does

The Agentic Stock Trader simulates an automated trading system that:

1. ✅ Fetches stock prices from external APIs
2. ✅ Analyzes market sentiment
3. ✅ Executes mock trades
4. ✅ Manages a portfolio
5. ✅ Saves data to a database
6. ✅ Uploads logs to cloud storage

All operations use hardcoded credentials that should be moved to Vault!

## Next Steps

After demonstrating the problem and Vault solution:

1. Show how to use Vault's dynamic secrets
2. Demonstrate secret rotation
3. Show audit logging in Vault
4. Discuss policy-based access control

## Support

For issues or questions about this demo application, refer to the main [README.md](README.md) for detailed documentation.

---

**Remember**: This application intentionally contains exposed secrets for demonstration purposes only. Never use real credentials or deploy this to production!