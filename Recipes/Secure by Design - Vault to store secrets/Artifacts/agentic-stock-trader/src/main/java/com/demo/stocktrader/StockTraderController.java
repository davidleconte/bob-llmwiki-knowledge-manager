package com.demo.stocktrader;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import java.util.*;

/**
 * Web Controller for Stock Trader UI
 */
@Controller
public class StockTraderController {
    
    private final TradingService tradingService;
    
    public StockTraderController() {
        this.tradingService = new TradingService();
    }
    
    @GetMapping("/")
    public String index(Model model) {
        model.addAttribute("secrets", tradingService.getExposedSecrets());
        return "index";
    }
    
    @PostMapping("/api/trade")
    @ResponseBody
    public Map<String, Object> executeTrade() {
        return tradingService.runTradingSession();
    }
    
    @GetMapping("/api/portfolio")
    @ResponseBody
    public Map<String, Object> getPortfolio() {
        return tradingService.getPortfolioData();
    }
    
    @GetMapping("/api/secrets")
    @ResponseBody
    public Map<String, Object> getSecrets() {
        return tradingService.getExposedSecrets();
    }
}

// Made with Bob
