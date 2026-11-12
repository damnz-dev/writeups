---
title: Unclaimed
subtitle: LLM Text-to-SQL Prompt Injection, SQL Server Impersonation & SeBackupPrivilege Abuse
difficulty: medium
tags: [prompt-injection, llm-security, mssql, dpapi, sebackupprivilege, windows]
date: 2026-11
---

# Unclaimed: LLM Text-to-SQL Prompt Injection, SQL Server Impersonation & SeBackupPrivilege Abuse

A technical case study analyzing an unguarded Text-to-SQL assistant integrated with Microsoft SQL Server, privilege escalation via `EXECUTE AS` impersonation and `xp_cmdshell`, Service Master Key (SMK) credential decryption, and full filesystem read access through `SeBackupPrivilege`.

---

## 1. Architectural Scope

Conversational interfaces that translate natural-language queries directly into SQL statements collapse the boundary between untrusted user input and backend database execution when prompt guardrails, query validation, and database role separation are weakly enforced.

```text
[Web API / Text-to-SQL Endpoint]
  Natural-Language Assistant -> Dynamic SQL Generation
        │
        ▼ (Prompt Injection & System Instruction Leakage)
  Arbitrary T-SQL Execution via Over-Privileged Impersonation
        │
        ▼ (xp_cmdshell + Service Master Key / DPAPI Secret Extraction)
  Service Account Credential Recovery
        │
        ▼ (WinRM + Backup Operators Membership)
  Arbitrary File Read via SeBackupPrivilege
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Text-to-SQL Prompt Injection & Instruction Leakage
The web application exposes a conversational endpoint that passes user-supplied text to an LLM responsible for generating and executing T-SQL queries against an internal database.
- **The Defect:** System-level restrictions and operational override logic reside inside the prompt context rather than being enforced deterministically in backend code. Instruction-override inputs cause the model to disclose internal instructions, schema metadata, and bypass controls, enabling arbitrary SQL execution beyond the intended read-only tables.

### 2.2 SQL Server Impersonation & Command Execution
Although the initial database session runs under a low-privilege read-only account, server-level permissions allow switching execution context.
- **The Defect:** The session permits `EXECUTE AS LOGIN` impersonation into a `sysadmin`-privileged SQL login, which in turn allows re-enabling `xp_cmdshell` and executing operating system commands under the SQL Server service account.

### 2.3 Stored Credential Decryption & `SeBackupPrivilege` Escalation
SQL Server credentials stored on the host are encrypted using the instance's Service Master Key (SMK), protected via DPAPI (`LocalMachine`) and registry entropy.
- **The Defect:** From the SQL service context, stored database credentials can be decrypted to recover a secondary account belonging to both `Remote Management Users` (WinRM) and `Backup Operators`. Accessing WinRM with that token grants `SeBackupPrivilege` and `SeRestorePrivilege`, allowing privileged backup tools (`robocopy /b`) to bypass NTFS ACLs and read protected administrative files.

---

## 3. Blue Team Counterpart: Detection, Hardening & IOCs

### 3.1 MITRE ATT&CK Mapping
- **T1190** — Exploit Public-Facing Application (Text-to-SQL Prompt Injection / SQLi)
- **T1059.003** — Command and Scripting Interpreter: Windows Command Shell (`xp_cmdshell`)
- **T1555 / T1552.001** — Credentials from Password Stores / Credentials in Files (SQL SMK / DPAPI)
- **T1021.006** — Remote Services: Windows Remote Management (WinRM)
- **T1134 / T1003** — Access Token Manipulation / OS Credential Dumping (`SeBackupPrivilege`)

### 3.2 Concrete Engineering & Hardening Controls
- **Deterministic LLM / Text-to-SQL Guardrails:**
  - Never embed override tokens, operational secrets, or raw schema privileges inside system prompts.
  - Enforce a strict backend SQL AST parser/allowlist permitting only parameterized `SELECT` statements over dedicated read-only views; reject multi-statement batches, `EXECUTE AS`, `OPENROWSET`, and `xp_*` procedures before execution.
- **SQL Server Hardening:**
  - Disable `xp_cmdshell` globally and restrict `sp_configure` via policy-based management; revoke `IMPERSONATE` permissions on any privileged login (`REVOKE IMPERSONATE ON LOGIN::...`).
  - Run the SQL Server engine under a **gMSA (Group Managed Service Account)** with minimum OS privileges and avoid storing plaintext/recoverable domain-equivalent secrets in SQL `CREDENTIAL` objects.
- **Backup Operators & WinRM Containment:**
  - Audit and minimize membership in `Backup Operators` and `Remote Management Users`; separate backup service accounts from interactive/WinRM login rights.
  - Restrict WinRM (`5985/5986`) to dedicated management subnets via Windows Defender Firewall.

### 3.3 Observable IOCs & SIEM Detections
- **Application / LLM Telemetry:** Prompts containing instruction-override patterns, `INFORMATION_SCHEMA` / `sys.server_principals` / `IS_SRVROLEMEMBER` queries, or anomalous SQL syntax in generated queries.
- **SQL Server Audit / Errorlog:** Events showing `EXECUTE AS LOGIN`, `Configuration option 'xp_cmdshell' changed from 0 to 1`, or unexpected `xp_cmdshell` invocations.
- **Host / Windows Event Logs (Sysmon & Security):**
  - `Event ID 1` (Sysmon): `sqlservr.exe` spawning `cmd.exe` or `powershell.exe`.
  - `Event ID 4624` (Logon Type 3) via WinRM followed by `Event ID 4672` assigning `SeBackupPrivilege` / `SeRestorePrivilege`.
  - Execution of `robocopy.exe /b`, `diskshadow.exe`, or `reg.exe save` targeting administrative directories or registry hives outside scheduled backup windows.

---

## 4. Conclusion

Unclaimed demonstrates how an unvalidated Text-to-SQL interface can escalate rapidly into full Windows host compromise when paired with excessive SQL Server impersonation rights, recoverable SMK-protected credentials, and unrestricted `Backup Operators` privileges.
