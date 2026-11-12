---
title: Scaffold
subtitle: Directory ACL Chaining, DCOM Lateral Movement & AD CS Weak Binding
difficulty: hard
tags: [active-directory, adcs, acl, dcom]
date: 2026-10
---

# Scaffold: Directory ACL Chaining, DCOM Lateral Movement & AD CS Weak Binding

An Active Directory architecture review tracing non-default object permissions (`AddSelf`, `GenericWrite`, `groupType` mutation), DCOM lateral execution, and unpatched AD CS certificate-mapping impersonation (ESC9/ESC10).

---

## 1. Architectural Scope

Enterprise deployment pipelines integrating Microsoft Deployment Toolkit (MDT) services with Active Directory often leave residual service credentials and delegated directory permissions scattered across operational OUs. Chaining subtle LDAP attribute modification rights with pre-hardening Certificate Authority defaults enables domain-wide elevation.

```
[Directory & Deployment Perimeter]
  Credential Reuse Between Deployment Account & Operator Context
        │
        ▼ (Delegated AddSelf & GenericWrite ACEs)
  Disabled Account Reactivation & Security/Distribution Group Mutation
        │
        ▼ (DCOM Object Activation on Domain Controller)
  Privileged Endpoint Management Execution Context
        │
        ▼ (Attribute Write Over UserPrincipalName + Weak Certificate Mapping)
  AD CS Certificate Forgery -> Domain Administrator TGT & Access
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Hardened Deployment Endpoints & ACL Path Discovery
While exposed MDT OData endpoints properly prohibited XML DTD resolution (mitigating traditional XXE leakage), auditing credential reuse across operational accounts unlocked valid directory identities possessing subtle discretionary access control entries (DACLs).
- **The Defect:** Non-standard LDAP permissions allow low-privilege operators to add themselves to management groups (`AddSelf`), clear account-disable bitflags in `userAccountControl` (`GenericWrite`), and flip directory `groupType` integers—neutralizing quarantine group enforcement while promoting distribution groups into security principals whose SIDs enter Kerberos PAC tokens.

### 2.2 DCOM Activation Over Unusable WinRM
Where WinRM endpoints enforce stricter remote management restrictions, DCOM automation objects remain reachable for members of endpoint management groups, providing non-interactive command execution under the target user context.

### 2.3 Weak AD CS Certificate Mapping via `userPrincipalName` (ESC9/ESC10)
Windows builds lacking strict strong-certificate-binding enforcement (`StrongCertificateBindingEnforcement`) evaluate client authentication certificates using UPN subject alternative names when explicit object SIDs are omitted from issued templates.
- **The Defect:** Delegated write permissions over another user's `userPrincipalName` attribute enable temporarily aliasing that principal to a high-value domain administrator account, enrolling a client authentication certificate via the standard `User` template, restoring the original attribute cleanly, and authenticating via PKINIT Kerberos as the impersonated administrator.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Directory ACL Hygiene** | Audit non-default `AddSelf`, `GenericWrite`, and `WriteProperty` (`groupType`, `userPrincipalName`) delegations continuously; separate quarantine enforcement via explicit logon policies rather than mutable groups. |
| **Service Credential Reuse** | Eliminate shared passwords across deployment automation and human operator accounts; enforce gMSA identities. |
| **AD CS Mapping Enforcement** | Enforce Full Enforcement Mode (`StrongCertificateBindingEnforcement = 2`) per KB5014754 so certificates require `szOID_NTDS_CA_SECURITY_EXT` SID extensions matching the target account. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1552.001** — Unsecured Credentials: Credentials in Files (MDT Deployment Shares)
- **T1098** — Account Manipulation (AD ACL Abuse: `AddSelf`, `GenericWrite`)
- **T1021.003** — Remote Services: Distributed Component Object Model (`MMC20.Application`)

### 4.2 Concrete Engineering & Hardening Controls
- **MDT / Deployment Share Hardening:** Restrict `DeploymentShare$` access by provisioning subnet/machine account and remove domain-join credentials from readable `CustomSettings.ini` / `Bootstrap.ini` files.
- **Active Directory ACL Auditing:** Continuously audit AD permissions (PingCastle / BloodHound) to remove non-admin `GenericWrite`, `WriteDacl`, and `AddSelf` rights over privileged groups or accounts.
- **DCOM Restriction:** Disable remote instantiation of unnecessary DCOM classes (`MMC20.Application`) via GPO/DCOM hardening and filter dynamic RPC from standard workstations.

### 4.3 Observable IOCs & SIEM Detections
- Reads of `CustomSettings.ini` or `Unattend.xml` from non-provisioning hosts.
- AD `Event ID 5136` / `4728` showing ACL or group membership changes by non-admin accounts.
- `mmc.exe -Embedding` spawning child processes via DCOM (`Event ID 1` Sysmon).

---

## 5. Conclusion

Scaffold highlights the compounding impact of delegated Active Directory ACL hygiene failures: individually innocuous directory attribute permissions unite with legacy AD CS UPN-based certificate mapping to deliver silent domain compromise.
