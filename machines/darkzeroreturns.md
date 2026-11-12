---
title: DarkZeroReturns
subtitle: CI/CD Runner Abuse, Kerberos Collision & Cross-Forest Trust Forgery
difficulty: hard
tags: [active-directory, cross-forest, kerberos, cicd]
date: 2026-11
---

# DarkZeroReturns: CI/CD Runner Abuse, Kerberos Collision & Cross-Forest Trust Forgery

An enterprise architecture assessment tracing an attack path from template-engine code execution on a web front end through self-hosted Git CI/CD runners, AD-integrated Linux identity collision, and cross-forest Kerberos trust escalation.

---

## 1. Architectural Scope

Hybrid enterprise environments often join Linux application and build nodes into an external Windows Active Directory forest that shares an inter-forest trust with a core corporate forest. Weaknesses in CI/CD trigger enforcement and Kerberos-to-POSIX identity mapping enable lateral movement across OS families and forest boundaries.

```
[Web Campaign Front End]
  Unsafe Template Evaluation
        │
        ▼ (Database Secret Extraction & SSH Access)
  Repository Audit Context -> Self-Hosted CI/CD Runner Manipulation
        │
        ▼ (Domain-Joined Linux Host Context)
  AD Principal Creation & Local Kerberos Switch-User Name Collision
        │
        ▼ (Privileged Linux Access -> Domain Backup Secrets)
  External Forest KDC Compromise (DCSync)
        │
        ▼ (Unfiltered Cross-Forest Trust Boundary)
  Forged Referral Ticket with Target Enterprise Group SID -> Core Forest DC
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Server-Side Template Evaluation & Secret Exposure
Campaign management endpoints passing untrusted input into server-side template compilation engines permit arbitrary code evaluation within the web runtime, exposing local SQLite credential stores that grant authenticated SSH access into internal audit groups.

### 2.2 CI/CD Runner Trigger & Workspace Execution Abuse
Self-hosted workflow runners registered under privileged service accounts inherit trust over repository branches and automation triggers.
- **The Defect:** Flaws in review-event trigger validation combined with shared host runner execution contexts allow repository collaborators to force workflow execution directly inside the runner's persistent service account on the build host rather than ephemeral isolated containers.

### 2.3 Active Directory / MIT Kerberos Name Collision (`ksu`)
When Linux hosts authenticate against Active Directory via Kerberos/SSSD without strict domain-qualified local mapping or authorization files:
- **The Defect:** A service principal ticket present in a shared credential cache permits creating a new directory account whose unqualified short name matches the local `root` account. Standard Kerberos utilities (`ksu`) evaluating short principal names without strict realm/authorization whitelists equate the directory identity with local uid `0`.

### 2.4 Inter-Forest Trust & Missing SID Filtering
Extracting backup secrets after local root escalation yields privileged credentials in the external forest, enabling directory replication (`DCSync`) of its `krbtgt` cryptographic keys.
- **The Defect:** The trust relationship into the core forest lacked strict SID filtering protections for privileged enterprise group identifiers, allowing forged inter-realm referrals carrying elevated target-forest group SIDs to be accepted for administrative SMB/registry access against the primary domain controller.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Template Rendering** | Enforce strict context sandboxing and avoid passing raw user strings as templates. |
| **CI/CD Runners** | Execute workflows exclusively inside ephemeral, unprivileged containers and restrict pull-request trigger permissions on protected runners. |
| **AD-Joined Linux Auth** | Enforce explicit `.k5login` rules, block principal collisions with privileged local POSIX accounts, and limit directory-write ACLs on migration OUs. |
| **Cross-Forest Trusts** | Enable strict SID Filtering and Selective Authentication across all forest trusts; monitor abnormal `krbtgt` replication and TGT referral anomalies. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1195.002** — Compromise Software Supply Chain (CI/CD Workflow Manipulation `CVE-2026-33937`)
- **T1552.004** — Unsecured Credentials: CI/CD Secrets

### 4.2 Concrete Engineering & Hardening Controls
- **CI/CD Engine & Trigger Hardening:** Patch the Git/CI platform against `CVE-2026-33937`; avoid `pull_request_target` when checking out untrusted fork code and enforce least-privilege `GITHUB_TOKEN` (`permissions: contents: read`).
- **Protected Environments:** Require manual maintainer approval before executing workflows from external contributors and isolate deployment secrets in protected environments.
- **Ephemeral Runners:** Use single-use, network-segmented runners with no persistent disk state or lateral access to internal infrastructure.

### 4.3 Observable IOCs & SIEM Detections
- Pull requests modifying `.github/workflows/*.yml` or `.gitea/workflows/` from external forks.
- Unexpected outbound network connections or environment-variable dumps in CI runner logs.

---

## 5. Conclusion

DarkZeroReturns demonstrates how operational conveniences—persistent CI/CD build runners, permissive directory-to-POSIX name resolution, and unfiltered forest trusts—bridge isolated application flaws directly into full multi-forest domain compromise.
