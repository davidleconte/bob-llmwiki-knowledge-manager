---
title: Bob Shell UI Integration for Cost Tracking
category: guide
status: active
tags: [bob-shell, ui, cost-tracking, integration]
created: 2026-07-13
updated: 2026-07-13
---

# Bob Shell UI Integration for Cost Tracking

> ⚠️ **Frozen historical snapshot — retracted metrics.** This is a point-in-time planning/audit-trail document, preserved unedited below for the record. Any token-savings/quality figures it cites — e.g. "68.96%", "89.3%", "91.80%" — were **fabricated** (a simulation that never invoked the optimizer) and are **retracted**; the measured figure is ~20% optimizer compression (manifest-backed: `evaluation/results/validation-2026-07-14/`). See `STATUS.md` and `CHANGELOG.md` for current, provenance-backed numbers.


## Overview

This guide describes UI enhancements for Bob Shell to integrate the cost tracking system with visual feedback in the chat interface.

## Feature Request: Real-Time Cost Indicator

### Visual Indicator Specification

**Location:** End of chat input box  
**Icon:** 💰 or $ symbol  
**Color:** Blue (#0066CC or similar)  
**Behavior:** Shows when cost tracking is active

### Implementation Concept

```typescript
// Bob Shell UI Component (pseudo-code)
interface CostTrackingIndicator {
  // Visual properties
  icon: "💰" | "$";
  color: "blue";
  position: "end-of-chatbox";
  
  // State
  isActive: boolean;
  currentCost: number;
  savings: number;
  
  // Behavior
  onClick: () => void; // Show detailed cost dashboard
  onHover: () => void; // Show tooltip with quick stats
}

// Example implementation
const CostIndicator = () => {
  const [tracking, setTracking] = useState(false);
  const [stats, setStats] = useState({ cost: 0, savings: 0 });
  
  return (
    <div className="cost-indicator" style={{ color: 'blue' }}>
      {tracking && (
        <Tooltip content={`Cost: ${stats.cost} BC | Saved: ${stats.savings} BC`}>
          <span onClick={showDashboard}>💰</span>
        </Tooltip>
      )}
    </div>
  );
};
```

### User Experience Flow

1. **Activation**
   - User enables cost tracking in settings
   - Blue $ indicator appears at end of chat box
   - Indicator is always visible when tracking is active

2. **Hover Interaction**
   - Shows tooltip with quick stats:
     ```
     💰 Cost Tracking Active
     Session Cost: 2.45 BC
     Saved: 1.23 BC (33% efficiency)
     Budget: 1000 BC (0.2% used)
     ```

3. **Click Interaction**
   - Opens detailed cost dashboard modal/panel
   - Shows full breakdown:
     - Session overview
     - Cost by operation type
     - Savings breakdown
     - Budget status
     - Efficiency metrics

4. **Real-Time Updates**
   - Indicator updates after each exchange
   - Color changes based on budget status:
     - Blue: Healthy (<50% budget used)
     - Yellow: Warning (50-75% budget used)
     - Orange: Caution (75-90% budget used)
     - Red: Critical (>90% budget used)

### Visual Design Mockup

```
┌─────────────────────────────────────────────────────────────┐
│ Bob Shell                                              [💰]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: What is machine learning?                           │
│                                                             │
│  Bob: Machine learning is...                               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Type your message...                                   💰  │
└─────────────────────────────────────────────────────────────┘
                                                          ↑
                                              Blue $ indicator
                                              (clickable)
```

### Integration with Cost Tracking System

```python
# Backend integration (Bob Shell server)
from examples.live_session_tracker import LiveSessionTracker

class BobShellSession:
    def __init__(self):
        self.cost_tracker = LiveSessionTracker(
            session_id=f"bob-{datetime.now().isoformat()}",
            budget_bobcoins=1000.0
        )
        
    def process_message(self, user_message: str) -> dict:
        # Generate response
        assistant_response = self.generate_response(user_message)
        
        # Track costs
        exchange = self.cost_tracker.track_exchange(
            user_message=user_message,
            assistant_response=assistant_response,
            tool_uses=self.extract_tool_uses(assistant_response)
        )
        
        # Get current stats for UI
        savings = self.cost_tracker.get_savings_breakdown()
        budget = self.cost_tracker.tracker.get_budget_status()
        
        return {
            "response": assistant_response,
            "cost_tracking": {
                "active": True,
                "session_cost": budget['spent_bobcoins'],
                "session_savings": budget['saved_bobcoins'],
                "budget_percent": budget['percent_used'],
                "budget_status": self.get_budget_status_color(budget['percent_used'])
            }
        }
    
    def get_budget_status_color(self, percent_used: float) -> str:
        if percent_used < 50:
            return "blue"
        elif percent_used < 75:
            return "yellow"
        elif percent_used < 90:
            return "orange"
        else:
            return "red"
```

### Frontend Integration

```typescript
// Bob Shell UI (React/TypeScript)
interface CostTrackingState {
  active: boolean;
  sessionCost: number;
  sessionSavings: number;
  budgetPercent: number;
  budgetStatus: 'blue' | 'yellow' | 'orange' | 'red';
}

const ChatInterface = () => {
  const [costTracking, setCostTracking] = useState<CostTrackingState>({
    active: false,
    sessionCost: 0,
    sessionSavings: 0,
    budgetPercent: 0,
    budgetStatus: 'blue'
  });
  
  const sendMessage = async (message: string) => {
    const response = await api.sendMessage(message);
    
    // Update cost tracking state
    if (response.cost_tracking) {
      setCostTracking(response.cost_tracking);
    }
  };
  
  return (
    <div className="chat-interface">
      <ChatMessages />
      <ChatInput 
        onSend={sendMessage}
        costIndicator={costTracking.active && (
          <CostIndicator 
            cost={costTracking.sessionCost}
            savings={costTracking.sessionSavings}
            status={costTracking.budgetStatus}
          />
        )}
      />
    </div>
  );
};
```

## Settings Integration

### Cost Tracking Settings Panel

```
┌─────────────────────────────────────────────────────────────┐
│ Settings > Cost Tracking                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ☑ Enable cost tracking                                     │
│                                                             │
│ Budget Settings:                                            │
│   Session Budget: [1000] Bobcoins                          │
│   Alert at: [50%] [75%] [90%]                              │
│                                                             │
│ UI Settings:                                                │
│   ☑ Show cost indicator in chat                            │
│   ☑ Show tooltip on hover                                  │
│   ☑ Color-code by budget status                            │
│                                                             │
│ Dashboard Settings:                                         │
│   ☑ Auto-open on budget alerts                             │
│   ☑ Show savings breakdown                                 │
│   ☑ Export session data                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Dashboard Modal

### Quick Stats View (Hover)

```
┌─────────────────────────────────────┐
│ 💰 Cost Tracking Active             │
├─────────────────────────────────────┤
│ Session Cost:    2.45 BC            │
│ Saved:           1.23 BC            │
│ Efficiency:      33.4%              │
│ Budget:          1000 BC (0.2%)     │
│                                     │
│ Click for details →                 │
└─────────────────────────────────────┘
```

### Full Dashboard View (Click)

```
┌─────────────────────────────────────────────────────────────┐
│ 💰 Session Cost Dashboard                            [×]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ SESSION OVERVIEW                                            │
│ ├─ Duration: 15m 32s                                       │
│ ├─ Exchanges: 12                                           │
│ └─ Operations: 48                                          │
│                                                             │
│ COST SUMMARY                                                │
│ ├─ Budget:     1000.0000 BC                                │
│ ├─ Spent:         2.4500 BC                                │
│ ├─ Saved:         1.2300 BC ⭐                             │
│ ├─ Net Cost:      1.2200 BC                                │
│ └─ Remaining:   997.7800 BC                                │
│                                                             │
│ [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.2%           │
│                                                             │
│ SAVINGS BREAKDOWN                                           │
│ ├─ Cache Hits:        0.8200 BC (66.7%)                   │
│ └─ Optimizations:     0.4100 BC (33.3%)                   │
│                                                             │
│ EFFICIENCY METRICS                                          │
│ ├─ ROI:              50.2%                                 │
│ ├─ Tokens Used:      2,450                                 │
│ ├─ Tokens Saved:     1,230                                 │
│ └─ Avg Cost/Op:      0.0510 BC                             │
│                                                             │
│ [Export Data] [Reset Session] [Settings]                   │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Checklist

### Phase 1: Backend Integration
- [ ] Integrate LiveSessionTracker into Bob Shell server
- [ ] Add cost tracking to message processing pipeline
- [ ] Implement API endpoints for cost data
- [ ] Add WebSocket support for real-time updates

### Phase 2: UI Components
- [ ] Create CostIndicator component
- [ ] Implement tooltip with quick stats
- [ ] Build dashboard modal
- [ ] Add color-coding based on budget status

### Phase 3: Settings & Configuration
- [ ] Add cost tracking settings panel
- [ ] Implement budget configuration
- [ ] Add alert threshold settings
- [ ] Create export functionality

### Phase 4: Testing & Polish
- [ ] Test real-time updates
- [ ] Verify accuracy of cost calculations
- [ ] Test budget alerts
- [ ] Polish UI/UX

## API Endpoints

### Get Current Session Stats
```
GET /api/cost-tracking/session
Response:
{
  "active": true,
  "session_id": "bob-2026-07-13T01:00:00",
  "cost": 2.45,
  "savings": 1.23,
  "budget_percent": 0.2,
  "budget_status": "blue"
}
```

### Get Detailed Dashboard Data
```
GET /api/cost-tracking/dashboard
Response:
{
  "session": { ... },
  "costs": { ... },
  "savings": { ... },
  "efficiency": { ... }
}
```

### Export Session Data
```
GET /api/cost-tracking/export
Response: JSON file download
```

## Benefits

1. **Transparency**: Users see costs in real-time
2. **Awareness**: Visual feedback on budget usage
3. **Control**: Easy access to detailed breakdown
4. **Optimization**: Users can adjust behavior based on costs
5. **Trust**: Clear visibility into system efficiency

## Next Steps

1. **Bob Shell Developers**: Review this specification
2. **Design Team**: Create detailed UI mockups
3. **Backend Team**: Implement cost tracking integration
4. **Frontend Team**: Build UI components
5. **QA Team**: Test end-to-end functionality

---

*This feature request was created based on user feedback during cost tracking system development.*
