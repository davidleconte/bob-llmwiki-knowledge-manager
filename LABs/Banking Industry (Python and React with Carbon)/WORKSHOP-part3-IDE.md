# IBM Bob Workshop - Security Issue Discovery and Remediation | Part 3
## Case Study: GFM Bank Data Pipeline Security Audit (Python)

### Audience
Security engineers, DevSecOps professionals, and developers responsible for secure coding practices in banking and financial services applications.

### Goal of the Workshop
Demonstrate how **IBM Bob** can:
- Discover security vulnerabilities in code
- Categorize issues by severity and type (OWASP, CWE)
- Generate comprehensive security audit reports
- Propose secure code fixes
- Document remediation strategies for compliance

We will audit the **GFM Bank data pipeline** code, which contains intentional security vulnerabilities for training purposes.

### Bob IDE Mode
> **Required Mode:** `Code`
>
> Ensure you are in **Code Mode** before starting this lab. This mode provides optimal support for security analysis and code review.

---

## Workshop Flow Overview

1. Discover security vulnerabilities in the codebase
2. Categorize and document each vulnerability
3. Generate a comprehensive security audit report
4. Apply secure code fixes
5. Verify remediation effectiveness

Each step builds on the previous one and mirrors how security audits are conducted in real enterprise environments.

---

## Lab Files

The following files are included in this lab for security analysis:
- `code/data_pipeline.py` - Data engineering pipeline with intentional vulnerabilities
- `code/synthetic_generator.py` - Synthetic data generator with intentional vulnerabilities

> **Note:** These files contain **intentional security vulnerabilities** for educational purposes. The vulnerabilities include SQL injection, command injection, insecure deserialization, hardcoded credentials, and more.

---

## Step A - Discover Security Vulnerabilities

### Why this step?
The first step in any security audit is comprehensive vulnerability discovery. IBM Bob can analyze code to identify security issues that might be missed by traditional static analysis tools.

### Prompt
```
Analyze the code files in this project for security vulnerabilities. Identify all security issues, categorize them by type (OWASP Top 10, CWE), and rank them by severity (Critical, High, Medium, Low).

For each vulnerability found, provide:
1. Location (file and line number)
2. Vulnerability type and category
3. Description of the security risk
4. Potential attack scenario
5. Severity rating with justification
```

### Expected Findings

The codebase should reveal vulnerabilities including:

**data_pipeline.py:**
- Hardcoded credentials (CWE-798)
- SQL Injection via string formatting (CWE-89)
- Command injection via shell=True (CWE-78)
- Insecure deserialization with pickle (CWE-502)
- Disabled SSL verification (CWE-295)
- Overly permissive file permissions (CWE-732)

**synthetic_generator.py:**
- Hardcoded JWT secret (CWE-798)
- Insecure randomness for tokens (CWE-330)
- Arbitrary code execution via eval/exec (CWE-94)
- Weak password hashing with MD5 (CWE-328)
- Secrets written to disk in plaintext (CWE-312)
- Command injection (CWE-78)

---

## Step B - Generate Security Audit Report

### Why this step?
A formal security audit report is essential for:
- Compliance requirements (PCI-DSS, SOC2, ISO 27001)
- Risk management and prioritization
- Developer guidance and training
- Executive communication
- Audit trail documentation

### Prompt
```
Generate a comprehensive SECURITY_AUDIT_REPORT.md document that includes:

1. **Executive Summary**
   - Overview of files analyzed
   - Total vulnerabilities found by severity
   - Overall risk assessment
   - Key recommendations

2. **Vulnerability Inventory**
   For each vulnerability:
   - Unique ID (e.g., VULN-001)
   - File and line number
   - Vulnerability title
   - CWE/OWASP classification
   - Severity rating (Critical/High/Medium/Low)
   - CVSS score estimate (if applicable)
   - Detailed description
   - Proof of concept / attack scenario
   - Business impact
   - Remediation recommendation
   - Remediation effort estimate

3. **Risk Matrix**
   - Visual representation of vulnerabilities by severity and likelihood

4. **Remediation Roadmap**
   - Prioritized list of fixes
   - Suggested implementation order
   - Dependencies between fixes

5. **Secure Coding Guidelines**
   - Best practices to prevent similar issues
   - Language-specific recommendations for Python

Save this as SECURITY_AUDIT_REPORT.md in the current directory.
```

---

## Step C - Document Individual Vulnerabilities

### Why this step?
Detailed vulnerability documentation helps developers understand the issues and implement correct fixes.

### Prompt
```
For the top 5 most critical vulnerabilities found, create detailed documentation that includes:

1. **SQL Injection in data_pipeline.py**
   - Show the vulnerable code
   - Explain why it's vulnerable
   - Demonstrate a potential exploit
   - Show the secure fix using parameterized queries

2. **Command Injection vulnerabilities**
   - Identify all instances of shell=True
   - Explain the risks
   - Provide secure alternatives using subprocess with lists

3. **Insecure Deserialization (pickle)**
   - Explain the remote code execution risk
   - Show how an attacker could exploit this
   - Recommend safe alternatives (JSON, safe serialization)

4. **Hardcoded Secrets**
   - List all hardcoded credentials and secrets
   - Explain the risks of exposure
   - Show how to use environment variables or secret managers

5. **Cryptographic Weaknesses**
   - Identify weak hashing (MD5) and insecure randomness
   - Explain why these are insufficient for security
   - Provide modern, secure alternatives
```

---

## Step D - Apply Security Fixes

### Why this step?
Demonstrating the ability to not only identify but also fix security issues is crucial for practical security engineering.

### Prompt
```
Fix all security vulnerabilities in the codebase. For each fix:

1. Apply the secure coding pattern
2. Add comments explaining the security improvement
3. Ensure the fix doesn't break existing functionality
4. Follow Python security best practices

Specifically:
- Replace string formatting in SQL with parameterized queries
- Replace shell=True with subprocess using argument lists
- Remove or externalize hardcoded credentials
- Replace pickle with JSON for serialization
- Enable SSL verification in requests
- Fix file permissions to restrictive values (0o600)
- Replace MD5 with SHA-256 or bcrypt for password hashing
- Use secrets module instead of random for tokens
- Remove eval/exec or implement strict sandboxing
- Use secure JWT configuration with external secrets

Create the fixed versions of:
- data_pipeline_secure.py
- synthetic_generator_secure.py
```

---

## Step E - Verify Remediation

### Why this step?
After applying fixes, verification ensures the vulnerabilities are properly addressed.

### Prompt
```
Review the fixed code files and verify that:

1. All identified vulnerabilities have been addressed
2. No new security issues have been introduced
3. The code still functions correctly
4. Security best practices are followed

Generate a REMEDIATION_VERIFICATION.md document that includes:
- Checklist of all vulnerabilities and their fix status
- Any remaining concerns or recommendations
- Suggestions for additional security hardening
- Recommendations for security testing (SAST, DAST, penetration testing)
```

---

## Vulnerability Categories Covered

### OWASP Top 10 (2021)
| Category | Vulnerabilities in Lab |
|----------|----------------------|
| A01:2021 – Broken Access Control | N/A in this lab |
| A02:2021 – Cryptographic Failures | Weak hashing (MD5), hardcoded secrets |
| A03:2021 – Injection | SQL injection, Command injection, Code injection |
| A04:2021 – Insecure Design | Using eval/exec for transforms |
| A05:2021 – Security Misconfiguration | Disabled SSL, permissive file permissions |
| A06:2021 – Vulnerable Components | N/A in this lab |
| A07:2021 – Authentication Failures | Hardcoded credentials |
| A08:2021 – Data Integrity Failures | Insecure deserialization (pickle) |
| A09:2021 – Logging Failures | N/A in this lab |
| A10:2021 – SSRF | N/A in this lab |

### CWE Categories
| CWE ID | Description | Found In |
|--------|-------------|----------|
| CWE-78 | OS Command Injection | Both files |
| CWE-89 | SQL Injection | data_pipeline.py |
| CWE-94 | Code Injection (eval/exec) | synthetic_generator.py |
| CWE-295 | Improper Certificate Validation | data_pipeline.py |
| CWE-312 | Cleartext Storage of Sensitive Info | synthetic_generator.py |
| CWE-328 | Use of Weak Hash | synthetic_generator.py |
| CWE-330 | Use of Insufficiently Random Values | synthetic_generator.py |
| CWE-502 | Deserialization of Untrusted Data | data_pipeline.py |
| CWE-732 | Incorrect Permission Assignment | data_pipeline.py |
| CWE-798 | Use of Hard-coded Credentials | Both files |

---

## Expected Outcomes

By the end of this lab, you should have:

1. **SECURITY_AUDIT_REPORT.md** containing:
   - Complete vulnerability inventory
   - Risk assessment and prioritization
   - Remediation roadmap
   - Secure coding guidelines

2. **Secure code versions**:
   - data_pipeline_secure.py
   - synthetic_generator_secure.py

3. **REMEDIATION_VERIFICATION.md** containing:
   - Fix verification checklist
   - Remaining recommendations
   - Testing guidance

4. Understanding of how IBM Bob can:
   - Identify security vulnerabilities in code
   - Categorize issues using industry standards
   - Generate compliance-ready documentation
   - Apply secure coding fixes
   - Verify remediation effectiveness

---

## Best Practices Learned

### Secure Coding Patterns

1. **Input Validation**
   - Always validate and sanitize user input
   - Use allowlists over denylists

2. **Parameterized Queries**
   - Never use string formatting for SQL
   - Use prepared statements or ORMs

3. **Command Execution**
   - Avoid shell=True
   - Use subprocess with argument lists
   - Validate and sanitize command arguments

4. **Secrets Management**
   - Never hardcode credentials
   - Use environment variables or secret managers
   - Rotate secrets regularly

5. **Cryptography**
   - Use strong, modern algorithms
   - Use secrets module for random values
   - Properly manage keys and certificates

6. **Serialization**
   - Avoid pickle for untrusted data
   - Use JSON or other safe formats
   - Validate deserialized data

7. **File Operations**
   - Use restrictive file permissions
   - Validate file paths
   - Avoid writing secrets to disk

---

## Next Steps

After completing this lab:

1. **Apply learnings** to your own codebases
2. **Integrate security scanning** into CI/CD pipelines
3. **Train development teams** on secure coding practices
4. **Establish security review processes** for code changes
5. **Regular security audits** using tools like IBM Bob

---

## Additional Resources

- OWASP Top 10: https://owasp.org/Top10/
- CWE Database: https://cwe.mitre.org/
- Python Security Best Practices: https://python.org/dev/security/
- NIST Secure Software Development Framework: https://csrc.nist.gov/Projects/ssdf
