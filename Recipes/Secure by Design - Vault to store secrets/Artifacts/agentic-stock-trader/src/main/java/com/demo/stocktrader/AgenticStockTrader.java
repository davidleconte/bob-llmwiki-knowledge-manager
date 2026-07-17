package com.demo.stocktrader;

import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Agentic Stock Trader - Demo Application with Hardcoded Secrets
 * WARNING: This code contains intentionally exposed secrets for demonstration purposes
 */
public class AgenticStockTrader {
    
    // HARDCODED SECRETS - DO NOT USE IN PRODUCTION!
    private static final String ALPHA_VANTAGE_API_KEY = "AV_DEMO_KEY_12345ABCDEFGHIJKLMNOP";
    private static final String FINNHUB_API_KEY = "c8q2pr48v3i9fjqc8q2pr48v3i9fjqc8";
    private static final String POLYGON_API_KEY = "PKG_demo_key_987654321_ABCDEFGH";
    private static final String TRADING_API_SECRET = "sk_live_51HyperSecretTradingKey789XYZ";
    
    // Database credentials - EXPOSED!
    private static final String DB_HOST = "localhost";
    private static final String DB_PORT = "5432";
    private static final String DB_NAME = "stocktrader_db";
    private static final String DB_USERNAME = "admin";
    private static final String DB_PASSWORD = "SuperSecret123!@#";
    
    // AWS credentials for cloud storage - EXPOSED!
    private static final String AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE";
    private static final String AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";
    
    private Map<String, StockPosition> portfolio;
    private double cashBalance;
    
    public AgenticStockTrader() {
        this.portfolio = new HashMap<>();
        this.cashBalance = 100000.00; // Starting with $100k
        System.out.println("=== Agentic Stock Trader Initialized ===");
        System.out.println("Starting Balance: $" + String.format("%.2f", cashBalance));
    }
    
    /**
     * Simulates fetching real-time stock price from external API
     */
    public double getStockPrice(String symbol) {
        System.out.println("\n[API CALL] Fetching price for " + symbol);
        System.out.println("Using API Key: " + ALPHA_VANTAGE_API_KEY);
        
        // Simulate API call with random price
        double basePrice = 100.0 + (Math.random() * 400);
        System.out.println("Current price for " + symbol + ": $" + String.format("%.2f", basePrice));
        return basePrice;
    }
    
    /**
     * Simulates fetching market sentiment from Finnhub API
     */
    public String getMarketSentiment(String symbol) {
        System.out.println("\n[API CALL] Fetching sentiment for " + symbol);
        System.out.println("Using Finnhub API Key: " + FINNHUB_API_KEY);
        
        String[] sentiments = {"BULLISH", "BEARISH", "NEUTRAL"};
        String sentiment = sentiments[(int)(Math.random() * sentiments.length)];
        System.out.println("Market sentiment: " + sentiment);
        return sentiment;
    }
    
    /**
     * Simulates executing a trade via trading platform API
     */
    public boolean executeTrade(String symbol, int shares, String action) {
        System.out.println("\n[TRADING API] Executing " + action + " order");
        System.out.println("Using Trading API Secret: " + TRADING_API_SECRET);
        System.out.println("Symbol: " + symbol + ", Shares: " + shares);
        
        double price = getStockPrice(symbol);
        double totalCost = price * shares;
        
        if (action.equals("BUY")) {
            if (totalCost > cashBalance) {
                System.out.println("ERROR: Insufficient funds!");
                return false;
            }
            cashBalance -= totalCost;
            portfolio.put(symbol, new StockPosition(symbol, shares, price));
            System.out.println("SUCCESS: Bought " + shares + " shares of " + symbol);
        } else if (action.equals("SELL")) {
            if (!portfolio.containsKey(symbol)) {
                System.out.println("ERROR: No position in " + symbol);
                return false;
            }
            cashBalance += totalCost;
            portfolio.remove(symbol);
            System.out.println("SUCCESS: Sold " + shares + " shares of " + symbol);
        }
        
        return true;
    }
    
    /**
     * Simulates saving portfolio to database
     */
    public void savePortfolioToDatabase() {
        System.out.println("\n[DATABASE] Connecting to database...");
        System.out.println("Host: " + DB_HOST + ":" + DB_PORT);
        System.out.println("Database: " + DB_NAME);
        System.out.println("Username: " + DB_USERNAME);
        System.out.println("Password: " + DB_PASSWORD);
        
        System.out.println("Saving portfolio data...");
        for (StockPosition position : portfolio.values()) {
            System.out.println("  - " + position);
        }
        System.out.println("Portfolio saved successfully!");
    }
    
    /**
     * Simulates uploading trading logs to AWS S3
     */
    public void uploadLogsToCloud() {
        System.out.println("\n[AWS S3] Uploading trading logs...");
        System.out.println("AWS Access Key ID: " + AWS_ACCESS_KEY_ID);
        System.out.println("AWS Secret Access Key: " + AWS_SECRET_ACCESS_KEY);
        System.out.println("Bucket: trading-logs-bucket");
        System.out.println("Logs uploaded successfully!");
    }
    
    /**
     * Displays current portfolio status
     */
    public void displayPortfolio() {
        System.out.println("\n=== PORTFOLIO SUMMARY ===");
        System.out.println("Cash Balance: $" + String.format("%.2f", cashBalance));
        System.out.println("\nPositions:");
        
        double totalValue = cashBalance;
        for (StockPosition position : portfolio.values()) {
            double currentPrice = getStockPrice(position.symbol);
            double positionValue = currentPrice * position.shares;
            totalValue += positionValue;
            System.out.println("  " + position.symbol + ": " + position.shares + 
                             " shares @ $" + String.format("%.2f", currentPrice) + 
                             " = $" + String.format("%.2f", positionValue));
        }
        
        System.out.println("\nTotal Portfolio Value: $" + String.format("%.2f", totalValue));
        System.out.println("========================\n");
    }
    
    /**
     * Main trading loop
     */
    public void runTradingSession() {
        System.out.println("\n*** Starting Automated Trading Session ***\n");
        
        String[] symbols = {"AAPL", "GOOGL", "MSFT", "TSLA", "IBM"};
        
        // Simulate some trades
        for (String symbol : symbols) {
            String sentiment = getMarketSentiment(symbol);
            
            if (sentiment.equals("BULLISH")) {
                executeTrade(symbol, 10, "BUY");
            }
        }
        
        // Display portfolio
        displayPortfolio();
        
        // Save to database
        savePortfolioToDatabase();
        
        // Upload logs to cloud
        uploadLogsToCloud();
        
        System.out.println("\n*** Trading Session Complete ***\n");
    }
    
    /**
     * Inner class to represent a stock position
     */
    static class StockPosition {
        String symbol;
        int shares;
        double purchasePrice;
        
        StockPosition(String symbol, int shares, double purchasePrice) {
            this.symbol = symbol;
            this.shares = shares;
            this.purchasePrice = purchasePrice;
        }
        
        @Override
        public String toString() {
            return symbol + ": " + shares + " shares @ $" + String.format("%.2f", purchasePrice);
        }
    }
    
    /**
     * Main entry point
     */
    public static void main(String[] args) {
        System.out.println("\n");
        System.out.println("╔════════════════════════════════════════════╗");
        System.out.println("║   AGENTIC STOCK TRADER - DEMO VERSION     ║");
        System.out.println("║   WARNING: Contains Hardcoded Secrets!    ║");
        System.out.println("╚════════════════════════════════════════════╝");
        System.out.println("\n");
        
        AgenticStockTrader trader = new AgenticStockTrader();
        trader.runTradingSession();
        
        System.out.println("\nApplication completed. Check logs for exposed secrets!");
    }
}

// Made with Bob
