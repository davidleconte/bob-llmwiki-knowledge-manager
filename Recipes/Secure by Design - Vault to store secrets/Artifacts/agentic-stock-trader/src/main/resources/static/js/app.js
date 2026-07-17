// Agentic Stock Trader - Frontend JavaScript

let isTrading = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Agentic Stock Trader UI loaded');
    
    // Set up event listeners
    document.getElementById('runTradeBtn').addEventListener('click', runTradingSession);
    document.getElementById('refreshBtn').addEventListener('click', refreshPortfolio);
    
    // Load initial portfolio data
    refreshPortfolio();
});

// Run a trading session
async function runTradingSession() {
    if (isTrading) return;
    
    isTrading = true;
    const btn = document.getElementById('runTradeBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Trading in progress...';
    
    try {
        const response = await fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Trading session failed');
        }
        
        const data = await response.json();
        updatePortfolioDisplay(data);
        
        // Show success message
        showNotification('Trading session completed successfully!', 'success');
        
    } catch (error) {
        console.error('Error running trading session:', error);
        showNotification('Error running trading session: ' + error.message, 'error');
    } finally {
        isTrading = false;
        btn.disabled = false;
        btn.textContent = '🚀 Run Trading Session';
    }
}

// Refresh portfolio data
async function refreshPortfolio() {
    try {
        const response = await fetch('/api/portfolio');
        
        if (!response.ok) {
            throw new Error('Failed to fetch portfolio');
        }
        
        const data = await response.json();
        updatePortfolioDisplay(data);
        
    } catch (error) {
        console.error('Error refreshing portfolio:', error);
        showNotification('Error refreshing portfolio: ' + error.message, 'error');
    }
}

// Update the portfolio display
function updatePortfolioDisplay(data) {
    // Update summary stats
    document.getElementById('cashBalance').textContent = formatCurrency(data.cashBalance);
    document.getElementById('totalValue').textContent = formatCurrency(data.totalValue);
    document.getElementById('positionCount').textContent = data.positions.length;
    
    // Update positions table
    const positionsContent = document.getElementById('positionsContent');
    
    if (data.positions.length === 0) {
        positionsContent.innerHTML = '<p class="empty-state">No positions yet. Click "Run Trading Session" to start trading!</p>';
    } else {
        let html = '';
        data.positions.forEach(position => {
            const profitLoss = (position.currentPrice - position.purchasePrice) * position.shares;
            const profitLossPercent = ((position.currentPrice - position.purchasePrice) / position.purchasePrice * 100).toFixed(2);
            const profitLossClass = profitLoss >= 0 ? 'profit' : 'loss';
            
            html += `
                <div class="position-item">
                    <div class="position-field">
                        <span class="position-label">Symbol</span>
                        <span class="position-value">${position.symbol}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Shares</span>
                        <span class="position-value">${position.shares}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Purchase Price</span>
                        <span class="position-value">${formatCurrency(position.purchasePrice)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Current Price</span>
                        <span class="position-value">${formatCurrency(position.currentPrice)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Total Value</span>
                        <span class="position-value">${formatCurrency(position.value)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">P/L</span>
                        <span class="position-value ${profitLossClass}">
                            ${formatCurrency(profitLoss)} (${profitLossPercent}%)
                        </span>
                    </div>
                </div>
            `;
        });
        positionsContent.innerHTML = html;
    }
    
    // Update activity log
    updateActivityLog(data.activityLog);
}

// Update activity log
function updateActivityLog(logs) {
    const activityLog = document.getElementById('activityLog');
    
    if (!logs || logs.length === 0) {
        activityLog.innerHTML = '<p class="empty-state">No activity yet. Run a trading session to see logs.</p>';
        return;
    }
    
    let html = '';
    logs.forEach(log => {
        // Highlight exposed secrets in red
        const isSecretExposed = log.includes('API Key') || log.includes('Secret') || 
                               log.includes('Password') || log.includes('Username') ||
                               log.includes('Access Key');
        
        const className = isSecretExposed ? 'secret-exposed' : '';
        html += `<p class="${className}">${escapeHtml(log)}</p>`;
    });
    
    activityLog.innerHTML = html;
    
    // Scroll to bottom
    activityLog.scrollTop = activityLog.scrollHeight;
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show notification
function showNotification(message, type = 'info') {
    // Simple console notification for now
    // Could be enhanced with a toast notification library
    if (type === 'error') {
        console.error(message);
    } else {
        console.log(message);
    }
}

// Add some CSS for profit/loss colors
const style = document.createElement('style');
style.textContent = `
    .profit {
        color: #48bb78 !important;
        font-weight: bold;
    }
    .loss {
        color: #f56565 !important;
        font-weight: bold;
    }
`;
document.head.appendChild(style);

// Made with Bob
