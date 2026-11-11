---
title: DutyBound
subtitle: Barcode Audit Injection, X11 Socket Hijacking & Systemd Path Eval
difficulty: medium
tags: [sqli, x11, systemd, linux]
date: 2026-11
---

# DutyBound: Barcode Audit Injection, X11 Socket Hijacking & Systemd Path Eval

An evaluation of airport kiosk infrastructure where structured IATA barcode fields bypass SQL parameterization, unauthenticated local display sockets expose desktop sessions, and reactive `systemd.path` triggers unsafely evaluate configuration files.

---

## 1. Architectural Scope

Point-of-sale and self-checkout kiosks frequently integrate domain-specific parsers (such as IATA Resolution 792 boarding pass decoders), backed by relational databases, local X11 graphical sessions, and automated service hooks.

```
[Web Checkout & Barcode Verification]
  Structured Boarding Pass Parser -> Audit Trail Persistence
        │
        ▼ (Unparameterized SQL Concatenation + Stacked Queries)
  Database OS Program Execution
        │
        ▼ (World-Writable Local X11 UNIX Socket)
  Kiosk Graphical Session Input Injection
        │
        ▼ (Group-Writable CSV + Unsanitized Shell Eval in systemd.path)
  Host Root Execution
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Stacked SQL Injection via Domain Barcode Fields
While checkout application logic uses structured Rust-backed parsing for aviation boarding pass metadata, optional trailing airline-audit fields are forwarded directly into an unparameterized SQL `INSERT` statement.
- **The Defect:** Escaping string delimiters combined with multi-statement support and overly broad PostgreSQL execution roles (`pg_execute_server_program`) allows SQL injection in audit logging to transition immediately into operating system command execution under the database service context.

### 2.2 Unauthenticated Local X11 Display Socket Exposure
Graphical kiosk deployments running legacy X11 sessions require explicit `Xauthority` cookie enforcement to prevent local cross-user interference.
- **The Defect:** Leaving the local X11 display UNIX domain socket world-accessible without authentication allows another unprivileged local service account (such as the database daemon) to attach to the active display server, inject synthetic keystrokes, and spawn processes inside the interactive kiosk user's security context.

### 2.3 Unsafe `eval` on Group-Writable Operational Data
Background automation pairs a `systemd.path` unit with a privileged helper script that recalculates pricing schedules whenever operational CSV data changes.
- **The Defect:** The pricing CSV carries group-write permissions for kiosk operational staff, and the privileged handler interprets parsed columns through shell `eval` expansion instead of structured typed parsing—turning any malformed CSV row into privileged command execution.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Database Audit Logging** | Enforce parameterized queries across all parser fields and revoke `pg_execute_server_program` and superuser roles from application DB accounts. |
| **Display Server Isolation** | Enforce strict MIT-MAGIC-COOKIE authentication (`xhost -`), restrict UNIX socket permissions, or migrate kiosks to Wayland compositors with client isolation. |
| **Privileged Automation** | Replace shell `eval` parsing in privileged scripts with strict typed CSV libraries (Python/Go) and restrict configuration write permissions strictly to root. |

---

## 4. Conclusion

DutyBound illustrates how input validation gaps in non-traditional surfaces—structured barcode trailers and internal operational spreadsheets—combine with permissive local IPC sockets to dismantle kiosk isolation end to end.
