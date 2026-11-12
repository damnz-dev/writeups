---
title: Responder
subtitle: Remote File Inclusion Coercion & NetNTLM Hash Recovery
difficulty: easy
tags: [rfi, ntlm, winrm, windows]
date: 2026-10
---

# Responder: Remote File Inclusion Coercion & NetNTLM Hash Recovery

An architectural breakdown of Windows UNC path resolution inside unsanitized PHP file-inclusion handlers, outbound NTLM challenge/response coercion, and remote management exposure.

---

## 1. Architectural Scope

Windows-hosted web applications frequently inherit PHP dynamic file-loading patterns for localized content switching. Unlike POSIX environments where remote file inclusion depends strictly on explicit URL wrappers, Windows APIs transparently interpret UNC network paths as SMB shares, triggering automatic outbound authentication.

```
[Web Application Perimeter (Windows Host)]
  Unsanitized Template/Language Inclusion Parameter
        │
        ▼ (UNC Path Coercion Over SMB)
  Outbound NetNTLMv2 Authentication Handshake Captured
        │
        ▼ (Weak Administrative Password Offline Recovery)
  Authenticated Windows Remote Management Session
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Local-to-Remote File Inclusion via Windows UNC Paths
Query parameters dynamically constructing filesystem paths without canonicalization allow both arbitrary local file disclosure (LFI) and remote share requests.
- **The Defect:** Supplying a network UNC target to a Windows file-open routine coerces the host operating system to initiate an outbound SMB connection toward the listener, automatically transmitting an NTLMv2 challenge/response exchange for the active account context.

### 2.2 Legacy Authentication & Weak Credential Hygiene
Because outbound SMB connections remain unfiltered at the perimeter and NTLM negotiation is permitted, captured challenge/response material can be audited offline. Weak administrative passwords combined with exposed WinRM management interfaces yield full administrative host control without memory corruption.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Dynamic File Inclusion** | Replace dynamic include paths with explicit allowlisted key-to-template mappings and reject path separators or UNC prefixes. |
| **Outbound SMB & NTLM** | Block outbound TCP 445 traffic at host and perimeter firewalls; restrict or disable NTLMv2 client authentication via Group Policy (`LmCompatibilityLevel` and NTLM outbound restrictions). |
| **Administrative Passwords** | Enforce high-entropy passphrase complexity and restrict Windows Remote Management access to dedicated bastion subnets. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1190** — Exploit Public-Facing Application (Remote File Inclusion)
- **T1557.001** — Adversary-in-the-Middle: NTLM Credential Capture
- **T1021.006** — Remote Services: WinRM (`5985/tcp`)

### 4.2 Concrete Engineering & Hardening Controls
- **Disable RFI Vectors:** Set `allow_url_include = Off` and `allow_url_fopen = Off` in `php.ini`, and validate template/language parameters against a strict static allowlist.
- **Egress SMB & WinRM Hardening:** Block outbound `445/tcp` from web servers to prevent NetNTLMv2 leakage, enforce **SMB Signing**, and restrict WinRM (`5985/5986`) to administrative subnets.

### 4.3 Observable IOCs & SIEM Detections
- Query parameters containing `http://` or UNC paths (`//...`) triggering outbound `445/tcp` SYN packets from the web host.
- WinRM (`Event ID 4624` Logon Type 3) logins from non-management IP ranges.

---

## 5. Conclusion

Responder demonstrates how a simple input validation flaw in PHP on Windows turns native OS network-share resolution into an effective credential-coercion vector when outbound SMB egress and NTLM are left unrestricted.
