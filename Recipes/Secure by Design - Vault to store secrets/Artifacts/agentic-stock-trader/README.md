# Agentic Stock Trader - Vault Demo Application

A demonstration Java application intentionally containing **hardcoded secrets** for showcasing HashiCorp Vault integration.

## ⚠️ WARNING

This application contains **INTENTIONALLY EXPOSED SECRETS** for demonstration purposes only. These include:

- API Keys (Alpha Vantage, Finnhub, Polygon, Trading API)
- Database credentials (username/password)
- AWS credentials (Access Key ID, Secret Access Key)

**DO NOT use this code in production or with real credentials!**

## Purpose

This application is designed to demonstrate:
1. How to identify exposed secrets in code
2. How to store secrets securely in HashiCorp Vault
3. How to refactor code to retrieve secrets from Vault instead of hardcoding them

## Exposed Secrets in the Code

The following secrets are hardcoded in `AgenticStockTrader.java`:

```java
// API Keys
ALPHA_VANTAGE_API_KEY = "AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP"
FINNHUB_API_KEY = "c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8"
POLYGON_API_KEY = "PKG_demo_key_987654321_ABCDEFGH"
TRADING_API_SECRET = "sk_live_51HyperSecretTradingKey789XYZ"

// Database Credentials
DB_USERNAME = "admin"
DB_PASSWORD = "SuperSecret123!@#"

// AWS Credentials
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

## Prerequisites

- Java 11 or higher
- Maven 3.6+
- Podman (or Docker)
- HashiCorp Vault (for the demo)

## Quick Start

### 1. Build the Application

```bash
cd agentic-stock-trader
chmod +x build.sh run.sh reset-to-exposed-secrets.sh
./build.sh
```

### 2. Run the Application

```bash
./run.sh
```

The application will:
- Simulate fetching stock prices from APIs (using hardcoded API keys)
- Execute mock trades
- Save portfolio to a database (using hardcoded credentials)
- Upload logs to AWS S3 (using hardcoded AWS credentials)

### 3. Observe the Exposed Secrets

Watch the console output - you'll see all the hardcoded secrets being printed during execution!

## Demo Workflow

### Before Starting Your Demo

Create a backup of the exposed secrets version:

```bash
./reset-to-exposed-secrets.sh backup
```

### During Your Demo

1. **Show the exposed secrets** - Run the application and point out the hardcoded credentials in the output
2. **Identify secrets in code** - Open `AgenticStockTrader.java` and show the hardcoded values
3. **Set up Vault** - Configure your local Vault instance
4. **Store secrets in Vault** - Move all secrets to Vault
5. **Refactor code** - Modify the application to retrieve secrets from Vault
6. **Rebuild and run** - Show the application working with Vault

### After Your Demo

Restore the original exposed secrets version for the next demo:

```bash
./reset-to-exposed-secrets.sh restore
./build.sh
```

## Reset Script Usage

The `reset-to-exposed-secrets.sh` script helps manage demo iterations:

```bash
# Create backup of exposed secrets version (do this FIRST!)
./reset-to-exposed-secrets.sh backup

# Check current status
./reset-to-exposed-secrets.sh status

# Restore exposed secrets version (after demo)
./reset-to-exposed-secrets.sh restore
```

## Project Structure

```
agentic-stock-trader/
├── src/main/java/com/demo/stocktrader/
│   └── AgenticStockTrader.java          # Main application with exposed secrets
├── pom.xml                               # Maven configuration
├── Dockerfile                            # Container build configuration
├── build.sh                              # Build script for Podman
├── run.sh                                # Run script for Podman
├── reset-to-exposed-secrets.sh          # Demo reset utility
└── README.md                             # This file
```

## What the Application Does

The Agentic Stock Trader simulates an automated trading system that:

1. **Fetches Stock Prices** - Calls external APIs to get current stock prices
2. **Analyzes Market Sentiment** - Retrieves market sentiment data
3. **Executes Trades** - Places buy/sell orders through a trading API
4. **Manages Portfolio** - Tracks stock positions and cash balance
5. **Persists Data** - Saves portfolio to a database
6. **Uploads Logs** - Stores trading logs in cloud storage (AWS S3)

All of these operations use hardcoded credentials that should be moved to Vault!

## Vault Integration Steps (For Your Demo)

1. **Install and start Vault**
   ```bash
   vault server -dev
   ```

2. **Store secrets in Vault**
   ```bash
   vault kv put secret/stocktrader/api \
     alpha_vantage_key="AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP" \
     finnhub_key="c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8" \
     polygon_key="PKG_demo_key_987654321_ABCDEFGH" \
     trading_secret="sk_live_51HyperSecretTradingKey789XYZ"
   
   vault kv put secret/stocktrader/database \
     username="admin" \
     password="SuperSecret123!@#"
   
   vault kv put secret/stocktrader/aws \
     access_key_id="AKIAIOSFODNN7EXAMPLE" \
     secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
   ```

3. **Modify the Java code** to retrieve secrets from Vault instead of using hardcoded values

4. **Rebuild and test** with Vault integration

## Troubleshooting

### Build fails
- Ensure Java 11+ and Maven are installed
- Check that you're in the `agentic-stock-trader` directory

### Podman not found
- Install Podman: https://podman.io/getting-started/installation
- Or use Docker by replacing `podman` with `docker` in the scripts

### Permission denied on scripts
```bash
chmod +x build.sh run.sh reset-to-exposed-secrets.sh
```

## License

This is a demonstration application for educational purposes only.

## Security Notice

🔒 **Remember**: This application intentionally contains exposed secrets for demonstration purposes. Never commit real secrets to version control or hardcode them in production applications. Always use a secrets management solution like HashiCorp Vault!