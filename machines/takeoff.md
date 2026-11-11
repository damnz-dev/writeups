---
title: Takeoff
subtitle: Go Template SSTI, Custom Binary Token Forgery & Container Bind Escapes
difficulty: hard
tags: [ssti, golang, containers, privesc]
date: 2026-11
---

# Takeoff: Go Template SSTI, Custom Binary Token Forgery & Container Bind Escapes

A deep-dive architectural analysis where Go `text/template` server-side injection leaks runtime environment secrets, unlocking exact HMAC forgery over dynamic `gob` binary streams, internal workflow automation RCE, and host escape across an unsafe Docker bind mount.

---

## 1. Architectural Scope

Airline reservation web apps written in Go/Echo often combine PDF document generation, HMAC-authenticated binary QR tickets, and internal loopback workflow automation (such as containerized `n8n` instances). Breaking template context isolation exposes environment variables governing cryptographic integrity across the entire stack.

```
[Web Booking Platform (Go / Echo)]
  PDF Rendering Engine Evaluating User Notes as Template Source
        │
        ▼ (Process Environment Disclosure via Template Context Method)
  Recovery of HMAC Signing Key & Internal Automation API JWT
        │
        ▼ (Exact Go `gob` Interface Encoding + Valid HMAC Forgery)
  Unauthenticated Check-In Endpoint Execution Sink
        │
        ▼ (Loopback Workflow Engine Execution in Privileged Container)
  Host Home Bind-Mount Misconfiguration -> SUID Escalation -> Host Root
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Go `text/template` SSTI Behind PDF Sanitization
Earlier audits verified that generated PDF syntax remained immune to raw PDF stream corruption (`gofpdf` escaping). However, the defect resided one tier earlier:
- **The Defect:** User-controlled booking note strings were compiled as executable Go `text/template` sources rather than passed safely as data parameters, exposing bound context helper methods capable of reading process environment memory cleanly into rendered PDFs.

### 2.2 Binary Protocol Fidelity (`gob`) & Dormant Execution Sinks
Because the check-in endpoint expected a binary Go `gob` payload signed with a 256-bit HMAC key, exhaustive offline brute-forcing failed entirely—and an internal command field remained unreachable without valid signatures.
- **The Defect:** Recovering the signing secret from process environment memory allowed exact byte-level reconstruction of dynamically registered Go interface structs (`gob.Register` + `EncodeValue`), turning an authenticated verification token check into remote command execution under the web service context.

### 2.3 Loopback Automation APIs & Container Host Bind Mounts
Using the secondary automation JWT recovered from environment variables enables creating and executing system-command workflow nodes on an internal `n8n` container running as container `root`.
- **The Defect:** Mounting a real host user home directory directly to `/root` inside the container breaks namespace isolation completely—allowing container-side file creation, SSH key injection, and SUID binary placement that yield immediate root privileges on the underlying host OS.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Template Compilation** | Never compile untrusted user strings via `template.Parse`; inject user fields strictly as template data arguments and remove filesystem helper methods from view contexts. |
| **Secret Isolation & Sinks** | Remove shell execution hooks completely from signed data models, inject secrets via scoped secret files or Vault rather than shared web-process environment variables. |
| **Container Storage & Users** | Run workflow containers as unprivileged non-root UIDs and never bind-mount host home directories or sensitive host paths into container root workspaces. |

---

## 4. Conclusion

Takeoff reinforces an essential principle in security architecture: validating outer serialization formats (like PDF syntax) provides false assurance if upstream template interpolation leaks cryptographic keys that activate dormant execution sinks and insecurely mounted automation containers.
