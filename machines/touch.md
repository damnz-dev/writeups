---
title: Touch
subtitle: Unauthenticated Hardware API, CSS Masking & Browser Kiosk Breakout
difficulty: easy
tags: [kiosk-escape, rdp, database-udf, windows]
date: 2026-10
---

# Touch: Unauthenticated Hardware API, CSS Masking & Browser Kiosk Breakout

A Windows kiosk security review examining unauthenticated peripheral management APIs, client-side DOM credential exposure, hardware-fault error workflows triggering restricted-shell escape, and MySQL User-Defined Function (`UDF`) elevation.

---

## 1. Architectural Scope

Self-service airport check-in terminals pair full-screen locked desktop shells over RDP with out-of-band hardware control hubs. Weak authentication on device management dashboards and unhardened error-recovery hyperlinks inside kiosk UIs collapse desktop lockdown controls.

```
[DeviceHub Management Interface]
  Unauthenticated Status Serial Disclosure -> Default Login Access
        │
        ▼ (Client-Side CSS-Only Credential Masking)
  Plaintext Kiosk RDP Credentials Recovered from HTML
        │
        ▼ (Hardware Fault State Triggering External Hyperlink)
  Restricted Browser Breakout -> Local File Picker -> OS Shell
        │
        ▼ (Local Batch Automation Secret -> Database Plugin Dir Write)
  MySQL UDF Dynamic Library Load -> NT AUTHORITY\SYSTEM
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Unauthenticated Serial Exposure & Client-Side Secret Masking
Out-of-band hardware monitoring portals often treat device serial numbers as low-sensitivity telemetry while simultaneously shipping factory passwords derived directly from that serial identifier.
- **The Defect:** Even after portal authentication, peripheral credentials rendered inside administrative views are concealed purely through CSS masking while remaining embedded in plaintext within inline JavaScript attributes—allowing trivial recovery of kiosk session logins reachable via non-NLA RDP.

### 2.2 Asynchronous Hardware Fault State Triggering Kiosk Escape
Within the full-screen check-in application, normal workflows trap all window focus and keyboard shortcuts cleanly.
- **The Defect:** Toggling scanner hardware offline via the external DeviceHub management API induces an unhandled peripheral fault state inside the check-in workflow, rendering an interactive support hyperlink. Activating that link launches Microsoft Edge outside the kiosk shell container, where native file-open dialogs expose arbitrary local binary execution under the kiosk account.

### 2.3 Cleartext Script Secrets & Database Plugin Elevation
Local maintenance batch files readable on disk retain privileged database credentials.
- **The Defect:** When the database service runs under `SYSTEM` with writable plugin directories (`plugin_dir`) and permissive `secure_file_priv` defaults, administrative database access enables deploying compiled MySQL User-Defined Functions (`UDF`) to execute operating system commands directly under the highest Windows privilege context.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Management Dashboards** | Enforce mandatory credential rotation away from device serial defaults, remove plaintext secrets from HTML DOM payloads, and require strong NLA/MFA for RDP endpoints. |
| **Kiosk Shell Hardening** | Disable external URL protocol handlers and native browser file pickers (`InPrivate`/AppLocker WDAC policies); handle hardware faults strictly inside locked modal views. |
| **Database Service Hardening** | Run MySQL under minimal virtual service accounts instead of `SYSTEM`, lock down `plugin_dir` ACLs, enforce `secure_file_priv`, and migrate automation secrets to credential vaults. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1078.001** — Valid Accounts: Default Accounts
- **T1021.001** — Remote Services: Remote Desktop Protocol (Kiosk Escape)
- **T1543** — Create or Modify System Process (MySQL UDF `sys_exec`)

### 4.2 Concrete Engineering & Hardening Controls
- **API Auth & Secret Removal:** Require authentication on all internal API routes, remove default credentials, and strip debug secrets from rendered HTML.
- **Kiosk & RDP Hardening:** Enforce NLA and firewall allowlists on `3389/tcp`; lock down kiosk accounts with **Assigned Access** and **AppLocker / WDAC** blocking `cmd.exe`, `powershell.exe`, and file/print escape dialogs.
- **MySQL Anti-UDF Hardening:** Set `secure_file_priv=""` in `my.ini`, run MySQL under a low-privilege account, and remove write permissions on `plugin_dir`.

### 4.3 Observable IOCs & SIEM Detections
- Unauthenticated requests to administrative API endpoints.
- `cmd.exe` or `explorer.exe` spawned under a kiosk user session (`Event ID 1` Sysmon).
- `.dll`/`.so` writes to MySQL `plugin_dir` or `CREATE FUNCTION ... SONAME` queries.

---

## 5. Conclusion

Touch illustrates how physical-digital convergence surfaces fail when hardware control APIs, frontend CSS obfuscation, kiosk error states, and over-privileged database engines interact across weak boundaries.
