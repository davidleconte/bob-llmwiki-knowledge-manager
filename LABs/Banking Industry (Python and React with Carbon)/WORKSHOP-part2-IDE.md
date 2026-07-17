# IBM Bob Workshop - Build a Carbon React Teller Application | Part 2
## Case Study: GFM Bank Modern Teller Interface (React / IBM Carbon Design)

### Audience
Frontend developers, full-stack engineers, and UI/UX professionals building modern banking interfaces with React and IBM Carbon Design System.

### Goal of the Workshop
Demonstrate how **IBM Bob** can:
- Generate complete React applications from requirements
- Apply IBM Carbon Design System components correctly
- Connect frontend applications to existing backend APIs
- Create production-ready, accessible banking interfaces
- Leverage MCP (Model Context Protocol) for enhanced design capabilities

We will build a modern **Teller Front-End** for GFM Bank that connects to the Core Banking API analyzed in Part 1.

### Bob IDE Mode
> **Required Mode:** `Carbon React`
>
> Ensure you are in **Carbon React Mode** before starting this lab. This mode provides enhanced support for React development with IBM Carbon Design System components.

---

## Prerequisites - Setup Instructions

### Step 1: Install Carbon React Mode from Bob Marketplace

Before starting this lab, you must install the **Carbon React Mode** from the Bob Marketplace:

1. Open IBM Bob IDE
2. Navigate to the **Marketplace** (usually accessible from the sidebar or menu)
3. Search for **"Carbon React"** mode
4. Click **Install** to add this mode to your Bob environment
5. Once installed, switch to **Carbon React Mode** from the mode selector

### Step 2: Install IBM Carbon MCP from IBM MCP Marketplace

For enhanced Carbon Design System support, install the IBM Carbon MCP:

1. Visit the IBM Carbon MCP onboarding page:
   **https://pages.github.ibm.com/carbon/ibm-products/developing/carbon-mcp/onboarding/**

2. Follow the onboarding instructions to:
   - Get your personal API key
   - Configure the MCP connection in Bob

3. Add your Carbon MCP key to Bob:
   - Open Bob settings
   - Navigate to MCP configuration
   - Add your IBM Carbon MCP key

4. Verify the MCP is connected before proceeding with the prompts

> **Important:** The Carbon React Mode combined with IBM Carbon MCP enables Bob to generate pixel-perfect Carbon Design System components with proper theming, accessibility, and banking-appropriate styling.

---

## Workshop Flow Overview

1. Test the existing backend API connectivity
2. Design and build the React application structure
3. Implement authentication and session management
4. Create the teller operations interface
5. Test the application with the embedded browser

Each step builds on the previous one to create a complete, production-ready banking teller interface.

---

## Lab Files

The following files are included in this lab for reference:
- `code/teller_client.py` - Reference CLI showing all required operations
- `code/backoffice_client.py` - Reference for understanding API patterns
- `code/requirements.txt` - Python dependencies (for reference)

Backend Server:
- **URL**: `https://wxo-corebanking-backend.1944johjccn7.eu-de.codeengine.appdomain.cloud`
- **Test IBAN**: `DE89545769475769453536`

---

## Step 1 - Test Backend Connectivity

### Why this step?
Before building a frontend, verify that the backend API is accessible and functioning correctly.

### Prompt
```
Can you test my teller client with my server:
https://wxo-corebanking-backend.1944johjccn7.eu-de.codeengine.appdomain.cloud

Use IBAN DE89545769475769453536 to check the balance.
```

### Expected Outcome
Bob should:
- Connect to the backend server
- Authenticate using the teller credentials
- Retrieve and display the account balance
- Show recent transactions for the specified IBAN

---

## Step 2 - Build the Carbon React Teller Application

### Why this step?
This is the main development step where Bob generates a complete React application with IBM Carbon Design System.

### Prompt (Basic)
```
OK, now based on the teller app, I want to create a Teller Front-End based on React with IBM Carbon design. Take into consideration the following aspects:

1. Name of the bank: "GFM Bank"
2. Have a login page with username: teller1 and password: password1 (taken from .env file)
3. After login, show a backend server status indicator in the top right corner (online/offline)
4. A modern interface for the Teller to interact with all the features defined in the teller_client.py
5. Design this with Banking usage in consideration
```

> **Tip:** Use Bob's **magic wand** feature to enhance this prompt for more detailed and comprehensive output.

### Prompt (Enhanced - Alternative)

Use this comprehensive prompt for a more detailed application:

```
Create a comprehensive React-based Teller Front-End application for GFM Bank using IBM Carbon Design System with the following specifications:

**Application Requirements:**
Develop a modern, professional banking teller interface that connects to the Core Banking backend server at https://wxo-corebanking-backend.1944johjccn7.eu-de.codeengine.appdomain.cloud

**Authentication System:**
- Implement a secure login page with IBM Carbon form components
- Store credentials in environment variables (.env file): username "teller1" and password "password1"
- Include proper form validation and error handling
- Add session management with secure token storage

**Main Dashboard Layout:**
- Display "GFM Bank" branding prominently in the header using IBM Carbon design tokens
- Position a real-time backend server status indicator in the top-right corner showing "Online" (green) or "Offline" (red/gray) with automatic health check polling
- Implement IBM Carbon's UI Shell component for consistent navigation and layout

**Teller Operations Interface:**
Replicate all functionality from the teller_client.py with modern UI components:
- Account balance inquiry with IBAN input and formatted currency display
- Customer account creation form with validation
- Money deposit interface with amount input and transaction confirmation
- Money withdrawal interface with balance verification
- Account-to-account transfer with dual IBAN inputs and amount specification
- Transaction history viewer with sortable, filterable data tables
- Account details lookup with comprehensive information display

**Design Considerations:**
- Apply IBM Carbon banking theme with professional color palette (blues, grays, whites)
- Use Carbon's data table components for transaction lists and account information
- Implement Carbon notifications for success/error messages
- Add loading states using Carbon skeleton components during API calls
- Ensure responsive design for various screen sizes
- Include proper error boundaries and fallback UI
- Add confirmation modals for critical operations (withdrawals, transfers)
- Display currency amounts with proper formatting (EUR symbol, decimal places)
- Implement form validation with real-time feedback
- Add accessibility features (ARIA labels, keyboard navigation)

**Technical Implementation:**
- Use React functional components with hooks
- Implement Axios or Fetch for API communication
- Add environment variable configuration for backend URL and credentials
- Include proper TypeScript types or PropTypes validation
- Structure components logically (pages, components, services, utils)
- Implement React Router for navigation between views
- Add state management (Context API or Redux) for user session and app state
- Include automated backend health checks with configurable intervals
- Handle API errors gracefully with user-friendly messages

**Security Features:**
- Implement JWT token handling if applicable
- Add automatic logout on session expiration
- Sanitize all user inputs
- Use HTTPS for all API communications
- Implement CORS handling

**Additional Features:**
- Add a dashboard summary showing key metrics
- Include quick action buttons for common teller operations
- Implement search functionality for customer accounts
- Add print receipt functionality for transactions
- Include audit trail logging for compliance

Provide complete, production-ready code with proper project structure, package.json with all dependencies (react, @carbon/react, react-router-dom, axios, dotenv), and clear setup instructions.
```

### Expected Outcome
Bob should generate:
- Complete React project structure
- All necessary components with IBM Carbon styling
- API service layer for backend communication
- Authentication flow with session management
- Responsive, accessible banking interface
- Setup instructions and package.json

---

## Step 3 - Test the Application

### Why this step?
Verify the generated application works correctly by running it in Bob's embedded browser.

### Prompt
```
Start the UI and test the web interface using the embedded browser. After login, find the latest transactions for the client with IBAN number: DE89545769475769453536
```

### Expected Outcome
Bob should:
- Start the React development server
- Open the application in the embedded browser
- Navigate through the login flow
- Display the transaction history for the specified IBAN
- Demonstrate the full functionality of the teller interface

---

## Application Features Checklist

After completing this lab, your application should include:

### Authentication
- [ ] Login page with IBM Carbon form components
- [ ] Environment variable-based credential configuration
- [ ] Session management with token storage
- [ ] Logout functionality

### Dashboard
- [ ] GFM Bank branding in header
- [ ] Server status indicator (online/offline)
- [ ] Navigation using Carbon UI Shell
- [ ] Quick action buttons

### Teller Operations
- [ ] Balance inquiry with IBAN lookup
- [ ] Transaction history with data tables
- [ ] Money transfer between accounts
- [ ] Overdraft request functionality
- [ ] Account details display

### User Experience
- [ ] Loading skeletons during API calls
- [ ] Success/error notifications
- [ ] Confirmation modals for critical actions
- [ ] Responsive design
- [ ] Accessibility compliance

---

## Troubleshooting

### Common Issues

**Carbon MCP not responding:**
- Verify your API key is correctly configured
- Check the MCP connection status in Bob settings
- Ensure you're in Carbon React Mode

**Backend connection failed:**
- Verify the backend URL is accessible
- Check for CORS issues in browser console
- Ensure credentials are correct

**Components not rendering correctly:**
- Verify all Carbon dependencies are installed
- Check for CSS import statements
- Review browser console for errors

---

## Next Steps

After completing this lab, proceed to:
- **Part 3**: Discover and fix security issues in banking code

You can also extend this application by:
- Adding additional back-office features
- Implementing customer management
- Adding transaction reporting
- Creating audit dashboards
