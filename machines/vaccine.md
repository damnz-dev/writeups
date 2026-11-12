---
title: Vaccine
subtitle: Legacy Archive Exposure, PostgreSQL Execution & Restricted Editor Escape
difficulty: easy
tags: [ftp, sqli, postgresql, linux]
date: 2026-10
---

# Vaccine: Legacy Archive Exposure, PostgreSQL Execution & Restricted Editor Escape

An end-to-end chain from anonymous FTP backup disclosure and weak archive encryption to authenticated SQL injection in PostgreSQL and `sudo` shell-escape via unrestricted interactive editors.

---

## 1. Architectural Scope

Legacy web deployments frequently archive application source code directly onto co-located file services protected solely by weak symmetric zip encryption. Source-code disclosure accelerates vulnerability discovery against backed PostgreSQL databases, leading into privilege escalation via interactive `sudo` misconfigurations.

```
[Perimeter File Service]
  Anonymous FTP Access -> Weakly Encrypted Source Backup Archive
        │
        ▼ (Offline Dictionary Recovery & Hardcoded App Hash Inspection)
  Authenticated Portal Session & Vulnerable Search Query
        │
        ▼ (PostgreSQL SQL Injection -> OS Command Execution)
  Unprivileged Database Runtime Shell & Config Secret Discovery
        │
        ▼ (Restricted `sudo` Interactive Text Editor Policy)
  Embedded Subshell Invocation -> Host Root Shell
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Backup Disclosure & Weak Symmetric Archive Encryption
Exposing development or site backups on anonymous FTP shares creates an immediate source-code disclosure vector when archives rely on legacy ZipCrypto weak passwords crackable via common dictionaries.
- **The Defect:** Inspecting extracted PHP application files exposes unsalted legacy MD5 administrative authentication hashes alongside unsanitized SQL search query concatenation against PostgreSQL.

### 2.2 PostgreSQL Stacked/Command Execution & `sudo` Editor Escapes
Authenticated access to vulnerable search endpoints enables PostgreSQL command execution (`COPY ... TO PROGRAM`) when database accounts possess elevated server program privileges, while plaintext database configuration scripts reveal reused local user credentials.
- **The Defect:** Granting unprivileged accounts `sudo` permission to invoke full-featured interactive text editors (`vi`) against configuration files fails to prevent shell-escape directives embedded within the editor runtime, allowing trivial elevation to root regardless of the target file argument.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Backup & File Exposure** | Disable anonymous FTP, relocate source archives out of public network shares, and authenticate passwords using Argon2id/bcrypt rather than raw MD5. |
| **SQL Query Construction** | Adopt parameterized prepared statements consistently and strip superuser/execution roles from web-facing PostgreSQL database users. |
| **Delegated Administration** | Avoid granting `sudo` permissions to interactive editors (`vi`, `nano`, `less`); use `sudoedit` (`sudo -e`) with `NOEXEC` enforced so configuration edits execute unprivileged. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1078** — Valid Accounts (Anonymous FTP Backup Exposure)
- **T1190** — Exploit Public-Facing Application (PostgreSQL `COPY ... PROGRAM`)
- **T1548.003** — Abuse Elevation Control Mechanism: `sudo vi`

### 4.2 Concrete Engineering & Hardening Controls
- **FTP & Backup Security:** Disable anonymous FTP (`anonymous_enable=NO` in `vsftpd.conf`), remove backups from public shares, and use AES-256 archive encryption.
- **PostgreSQL Hardening:** Parameterize queries and ensure application roles lack `pg_execute_server_program` privileges.
- **Sudoers Hardening:** Never allow interactive editors (`vi`, `vim`, `nano`) in `/etc/sudoers`; replace with `sudoedit` scoped to specific configuration files.

### 4.3 Observable IOCs & SIEM Detections
- Anonymous FTP downloads of `.zip`/`.bak` archives followed by web login attempts.
- PostgreSQL logs showing `COPY ... FROM/TO PROGRAM` execution.
- `/bin/sh` or `/bin/bash` spawned as a child process of `vi` running under `sudo`.

---

## 5. Conclusion

Vaccine reinforces foundational defensive hygiene: backup leakage, weak hashing, unparameterized database queries, and naive `sudo` editor delegations continue to chain reliably whenever defense-in-depth is neglected across tiers.
