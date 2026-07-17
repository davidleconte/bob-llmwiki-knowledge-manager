# IBM Bob Workshop - Core Banking Architecture & Code Understanding | Part 1
## Case Study: GFM Bank Core Banking System (Python / FastAPI)

### Audience
Banking software engineers, solution architects, and developers working with core banking systems, REST APIs, and financial transaction processing.

### Goal of the Workshop
Demonstrate how **IBM Bob** can:
- Understand complex banking system codebases
- Analyze API architecture and data flows
- Generate comprehensive engineering artifacts (diagrams, documentation)
- Reason about financial transaction logic and data integrity
- Produce architecture documentation suitable for stakeholders

We use the **GFM Bank Core Banking System**, a realistic banking demo application with a FastAPI backend, teller client, and back-office client.

### Bob IDE Mode
> **Required Mode:** `Code`
>
> Ensure you are in **Code Mode** before starting this lab. This mode provides optimal support for code analysis and documentation generation.

---

## Workshop Flow Overview

1. Understand the codebase structure
2. Generate architecture documentation with Mermaid diagrams
3. Document functional requirements
4. Analyze data flow and transaction pipeline
5. Identify system invariants and assumptions
6. Create comprehensive ARCHITECTURE.md document

Each step builds on the previous one and mirrors how banking software is documented in real enterprise projects.

---

## Lab Files

The following files are included in this lab:
- `code/demo_api.py` - Core Banking FastAPI backend server
- `code/teller_client.py` - Teller CLI for customer-facing operations
- `code/backoffice_client.py` - Back-office CLI for administrative operations
- `code/corebank.db` - SQLite database with sample data
- `code/Dockerfile` - Container deployment configuration

---

## Step A - Understand the Code

### Why this step?
Before documenting, extending, or auditing financial software, engineers must **fully understand how it works**:
- API endpoints and authentication
- Transaction processing logic
- Role-based access control
- Data integrity mechanisms
- Business rules and constraints

This step shows that IBM Bob can perform a **deep technical read** of banking software, not just summarize files.

### Prompt
```
Can you describe what this software is doing? In addition, can you show me the software architecture - a Mermaid diagram will be a good start.
```

#### Enhanced Prompt (use Bob's magic star to generate something similar):
```
Analyze the GFM Bank Core Banking codebase and provide a comprehensive explanation of its functionality, including:

1. **API Architecture**: How the FastAPI backend handles authentication (OAuth2), account management, and transaction processing
2. **Role-Based Access Control**: How TELLER and BACKOFFICE roles differ in their permissions and capabilities
3. **Transaction Processing**: The transfer logic including balance verification, overdraft handling, and the two-transaction debit/credit pattern
4. **Data Model**: The relationship between users, customers, accounts, and transactions tables
5. **Client Applications**: How teller_client.py and backoffice_client.py interact with the API

Additionally, create detailed Mermaid diagrams showing:
- System architecture with all components
- API endpoint structure and authentication flow
- Transaction processing sequence
- Data model relationships

Clearly state key invariants, business rules, and assumptions made by the code.
```

---

## Step B - Generate Architecture Document

### Why this step?
Enterprise banking systems require formal architecture documentation for:
- Regulatory compliance and audits
- Onboarding new team members
- System integration planning
- Change management processes

### Prompt
```
Based on your analysis, create a comprehensive ARCHITECTURE.md document that includes:

1. **Executive Summary**: One-paragraph overview of the system
2. **System Architecture**: High-level Mermaid diagram showing all components
3. **Component Descriptions**: Detailed explanation of each module
4. **API Reference**: All endpoints with their purposes and access controls
5. **Data Model**: Entity-relationship diagram using Mermaid
6. **Transaction Flow**: Sequence diagram for key operations (transfer, balance inquiry)
7. **Security Model**: Authentication, authorization, and data protection
8. **Functional Requirements**: List of supported business operations
9. **Non-Functional Requirements**: Performance, reliability, and scalability considerations
10. **Assumptions and Constraints**: Technical and business limitations

Save this as ARCHITECTURE.md in the current directory.
```

---

## Step C - Data Pipeline Analysis

### Why this step?
Understanding how data flows through a banking system is critical for:
- Performance optimization
- Debugging transaction issues
- Planning system extensions
- Ensuring audit compliance

### Prompt
```
Create a detailed data pipeline analysis that covers:

1. **Request Lifecycle**: From HTTP request to database commit
2. **Transaction States**: How transfers move through validation, execution, and confirmation
3. **Error Handling**: What happens when transactions fail at each stage
4. **Consistency Guarantees**: How the system ensures ACID properties
5. **Audit Trail**: What information is logged and stored for compliance

Include a Mermaid flowchart showing the complete data pipeline from client request to persisted transaction.
```

---

## Step D - Functional Requirements Extraction

### Why this step?
Documenting functional requirements helps stakeholders understand system capabilities without reading code.

### Prompt
```
Extract and document all functional requirements from the codebase:

1. **Teller Operations**:
   - What can a teller do?
   - What information can they access?
   - What are the limitations?

2. **Back-Office Operations**:
   - What administrative functions are available?
   - What privileged operations require BACKOFFICE role?

3. **Business Rules**:
   - Overdraft limits and enforcement
   - Transfer validation rules
   - Fee reversal constraints

Format this as a structured requirements document with clear acceptance criteria.
```

---

## Step E - System Invariants and Assumptions

### Why this step?
Identifying invariants helps prevent bugs and guides future development.

### Prompt
```
Identify and document all system invariants and assumptions:

1. **Data Invariants**: Rules that must always hold true in the database
2. **Business Invariants**: Financial rules that cannot be violated
3. **Security Invariants**: Access control rules that must be enforced
4. **Technical Assumptions**: What the code assumes about its environment

For each invariant, explain:
- What the invariant is
- Where in the code it's enforced
- What could go wrong if violated
```

---

## Expected Outcome

By the end of this lab, you should have:

1. A complete **ARCHITECTURE.md** document containing:
   - System overview with Mermaid architecture diagram
   - Component descriptions
   - API reference with all endpoints
   - Data model with ER diagram
   - Transaction flow sequence diagrams
   - Security model documentation
   - Functional requirements
   - Data pipeline analysis
   - System invariants and assumptions

2. A deep understanding of how IBM Bob can:
   - Analyze complex financial codebases
   - Generate professional documentation
   - Create accurate technical diagrams
   - Extract business requirements from code
   - Identify critical system invariants

---

## Next Steps

After completing this lab, proceed to:
- **Part 2**: Build a new Carbon React Teller Application using the analyzed API
- **Part 3**: Discover and fix security issues in banking code
