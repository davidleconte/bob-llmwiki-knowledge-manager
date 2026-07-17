package com.demo.stocktrader;

import org.springframework.stereotype.Service;
import java.util.*;

/**
 * Trading Service with Exposed Secrets
 */
@Service
public class TradingService {
    
    // HARDCODED SECRETS - DO NOT USE IN PRODUCTION!
    private static final String ALPHA_VANTAGE_API_KEY = "AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP";
    private static final String FINNHUB_API_KEY = "c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8";
    private static final String POLYGON_API_KEY = "PKG_demo_key_987654321_ABCDEFGH";
    private static final String TRADING_API_SECRET = "sk_live_51HyperSecretTradingKey789XYZ";
    
    private static final String DB_HOST = "localhost";
    private static final String DB_PORT = "5432";
    private static final String DB_NAME = "stocktrader_db";
    private static final String DB_USERNAME = "admin";
    private static final String DB_PASSWORD = "SuperSecret123!@#";
    
    private static final String AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE";
    private static final String AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";
    
    private Map<String, StockPosition> portfolio = new HashMap<>();
    private double cashBalance = 100000.00;
    private List<String> activityLog = new ArrayList<>();
    
    public Map<String, Object> getExposedSecrets() {
        Map<String, Object> secrets = new LinkedHashMap<>();
        
        Map<String, String> apiKeys = new LinkedHashMap<>();
        apiKeys.put("Alpha Vantage", ALPHA_VANTAGE_API_KEY);
        apiKeys.put("Finnhub", FINNHUB_API_KEY);
        apiKeys.put("Polygon", POLYGON_API_KEY);
        apiKeys.put("Trading API", TRADING_API_SECRET);
        secrets.put("apiKeys", apiKeys);
        
        Map<String, String> database = new LinkedHashMap<>();
        database.put("Host", DB_HOST + ":" + DB_PORT);
        database.put("Database", DB_NAME);
        database.put("Username", DB_USERNAME);
        database.put("Password", DB_PASSWORD);
        secrets.put("database", database);
        
        Map<String, String> aws = new LinkedHashMap<>();
        aws.put("Access Key ID", AWS_ACCESS_KEY_ID);
        aws.put("Secret Access Key", AWS_SECRET_ACCESS_KEY);
        secrets.put("aws", aws);
        
        return secrets;
    }
    
    public Map<String, Object> runTradingSession() {
        activityLog.clear();
        String[] symbols = {"AAPL", "GOOGL", "MSFT", "TSLA", "IBM"};
        
        for (String symbol : symbols) {
            String sentiment = getMarketSentiment(symbol);
            if (sentiment.equals("BULLISH")) {
                executeTrade(symbol, 10, "BUY");
            }
        }
        
        saveToDatabase();
        uploadToCloud();
        
        return getPortfolioData();
    }
    
    private String getMarketSentiment(String symbol) {
        activityLog.add("Fetching sentiment for " + symbol + " using Finnhub API Key: " + FINNHUB_API_KEY);
        String[] sentiments = {"BULLISH", "BEARISH", "NEUTRAL"};
        return sentiments[(int)(Math.random() * sentiments.length)];
    }
    
    private void executeTrade(String symbol, int shares, String action) {
        double price = getStockPrice(symbol);
        activityLog.add("Executing " + action + " order using Trading API Secret: " + TRADING_API_SECRET);
        
        if (action.equals("BUY")) {
            double totalCost = price * shares;
            if (totalCost <= cashBalance) {
                cashBalance -= totalCost;
                portfolio.put(symbol, new StockPosition(symbol, shares, price));
                activityLog.add("SUCCESS: Bought " + shares + " shares of " + symbol + " @ $" + String.format("%.2f", price));
            }
        }
    }
    
    private double getStockPrice(String symbol) {
        activityLog.add("Fetching price for " + symbol + " using Alpha Vantage API Key: " + ALPHA_VANTAGE_API_KEY);
        return 100.0 + (Math.random() * 400);
    }
    
    private void saveToDatabase() {
        activityLog.add("Connecting to database: " + DB_HOST + ":" + DB_PORT);
        activityLog.add("Database: " + DB_NAME + ", Username: " + DB_USERNAME + ", Password: " + DB_PASSWORD);
        activityLog.add("Portfolio saved to database");
    }
    
    private void uploadToCloud() {
        activityLog.add("Uploading logs to AWS S3");
        activityLog.add("AWS Access Key ID: " + AWS_ACCESS_KEY_ID);
        activityLog.add("AWS Secret Access Key: " + AWS_SECRET_ACCESS_KEY);
        activityLog.add("Logs uploaded successfully");
    }
    
    public Map<String, Object> getPortfolioData() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("cashBalance", cashBalance);
        
        List<Map<String, Object>> positions = new ArrayList<>();
        double totalValue = cashBalance;
        
        for (StockPosition position : portfolio.values()) {
            double currentPrice = getStockPrice(position.symbol);
            double positionValue = currentPrice * position.shares;
            totalValue += positionValue;
            
            Map<String, Object> pos = new LinkedHashMap<>();
            pos.put("symbol", position.symbol);
            pos.put("shares", position.shares);
            pos.put("purchasePrice", position.purchasePrice);
            pos.put("currentPrice", currentPrice);
            pos.put("value", positionValue);
            positions.add(pos);
        }
        
        data.put("positions", positions);
        data.put("totalValue", totalValue);
        data.put("activityLog", activityLog);
        
        return data;
    }
    
    static class StockPosition {
        String symbol;
        int shares;
        double purchasePrice;
        
        StockPosition(String symbol, int shares, double purchasePrice) {
            this.symbol = symbol;
            this.shares = shares;
            this.purchasePrice = purchasePrice;
        }
    }
}

// Made with Bob
