---
title: Orion
subtitle: CMS Behavior Injection, Session File Poisoning & Telnetd Option Abuse
difficulty: easy
tags: [cms, object-injection, session-poisoning, linux]
date: 2026-10
---

# Orion: CMS Behavior Injection, Session File Poisoning & Telnetd Option Abuse

A focused walkthrough of framework-level property injection paired with PHP session poisoning on the web tier, culminating in legacy loopback remote-login argument injection.

---

## 1. Architectural Scope

Content management platforms built on layered MVC frameworks frequently permit dynamic component configuration through request payloads. When untrusted keys override class instantiation types, server-side file-backed session stores become an executable include primitive.

```
[Web CMS Perimeter]
  Behavior Property Precedence Flaw -> Arbitrary Class Instantiation
        │
        ▼ (Unvalidated Request Persistence in PHP Session Files)
  Local File Inclusion via RBAC File Loader -> Web Shell Execution
        │
        ▼ (Environment & Bcrypt Database Secret Recovery)
  Authenticated Local User SSH Access
        │
        ▼ (Loopback Inetd Telnetd Environment Argument Injection)
  Unauthenticated Login Bypass -> Root Shell
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Framework Object Instantiation Precedence & Session Poisoning
Vulnerabilities spanning CMS image-transform actions and underlying Yii behavior assignment allow callers to supply a custom `__class` override alongside constructor arguments even when the outer wrapper validates the primary `class` attribute.
- **The Defect:** By writing compact PHP code payloads into request query parameters that get serialized unescaped into disk-backed PHP session files, an attacker can instantiate a file-loading RBAC manager pointing straight at the poisoned session file to achieve immediate code execution under the web runtime.

### 2.2 Secret Discovery & Legacy Loopback Services
Inspecting application environment configuration files reveals local database credentials, exposing user account hashes crackable offline to obtain SSH access.
- **The Defect:** Process inspection exposes a manually configured `inetd`-managed `telnetd` daemon listening exclusively on loopback. Vulnerable GNU inetutils versions pass client-supplied `USER` environment strings directly as command-line tokens to the underlying `/bin/login` binary, enabling flag injection (`-f`) over a PTY session to bypass password verification completely.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **CMS & Framework Hygiene** | Apply security patches for both CMS component validation and underlying Yii framework behavior property resolution. |
| **Session Isolation** | Move PHP session handlers out of predictable local disk paths (e.g., encrypted Redis) and disable filesystem `open_basedir` access across runtime temp dirs. |
| **Legacy Network Daemons** | Decommission legacy `telnetd`/`inetd` packages completely—even on loopback interfaces—and avoid reusable credentials across application databases and OS users. |

---

## 4. Conclusion

Orion demonstrates the danger of multi-layer framework trust flaws combined with obsolete system services: an edge object-instantiation bug bridges cleanly to loopback-only legacy daemons that should never exist in modern Linux deployments.
