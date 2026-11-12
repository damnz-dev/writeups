---
title: Paperwork
subtitle: Printer Job Language Traversal & UNIX Socket Descriptor Exposure
difficulty: easy
tags: [pjl, path-traversal, ipc, linux]
date: 2026-11
---

# Paperwork: Printer Job Language Traversal & UNIX Socket Descriptor Exposure

An examination of legacy print-daemon protocol abuses enabling arbitrary filesystem writes, paired with privileged file-descriptor passing over local UNIX domain sockets (`SCM_RIGHTS`).

---

## 1. Architectural Scope

Networked printing appliances and archival print gateways expose raw JetDirect/PJL streams alongside legacy line-printer daemons. When print-management interpreters run without chroot containment, filesystem primitives inside PJL expose the host directly.

```
[Perimeter Print Services]
  Unauthenticated Printer Job Language (PJL) Stream
        │
        ▼ (Missing Path Containment on File Read/Write Commands)
  Authorized SSH Key Placement -> Unprivileged Shell Access
        │
        ▼ (Unrestricted UNIX Domain Socket Ancillary Data)
  Privileged File Descriptor Receipt (SCM_RIGHTS)
        │
        ▼ (Direct Descriptor Read -> Credential Exposure)
  Host Root Escalation
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 PJL Filesystem Traversal & Unauthorized Persistence
Traditional PJL commands support firmware and font filesystem inspection (`FSUPLOAD`, `FSDOWNLOAD`) relative to a logical spool root.
- **The Defect:** Failing to canonicalize and sandbox relative path segments allows remote unauthenticated network callers to traverse out of the virtual spool partition, inspect local account home directories, and write authorized SSH public keys directly onto the host filesystem.

### 2.2 Insecure Ancillary Data (`SCM_RIGHTS`) Over Local Sockets
UNIX domain sockets allow processes to transfer open kernel file descriptors across process boundaries using `SCM_RIGHTS` control messages.
- **The Defect:** A privileged local service opens restricted credential material under elevated permissions and passes the active file descriptor over an overly permissive local socket accessible to unprivileged users. Receiving the descriptor grants immediate read access inside the client's address space, circumventing filesystem ACL protections on the underlying credential store.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Print Protocol Exposure** | Disable PJL filesystem commands, isolate print daemons inside read-only chroot jails/containers, and bind raw print ports only to trusted internal VLANs. |
| **UNIX Socket IPC** | Enforce strict socket filesystem permissions (`0600`/`0660`), validate peer credentials via `SO_PEERCRED` before passing descriptors, and avoid transferring privileged FDs across trust boundaries. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1190** — Exploit Public-Facing Application (PJL Path Traversal)
- **T1098.004** — Account Manipulation: SSH Authorized Keys
- **T1548** — Abuse Elevation Control Mechanism (`SCM_RIGHTS` FD Leak)

### 4.2 Concrete Engineering & Hardening Controls
- **Print Protocol Isolation:** Never expose LPD (`515/tcp`) or JetDirect/PJL (`9100/tcp`) outside dedicated print VLANs; disable filesystem PJL commands (`FSUPLOAD`, `FSDOWNLOAD`, `FSDIRLIST`) or confine the daemon with `AppArmor`/`chroot`.
- **Socket & File Descriptor Hygiene:** Enforce `0600` permissions on privileged Unix domain sockets and set `FD_CLOEXEC` (`O_CLOEXEC`) on sensitive descriptors before privilege transitions.

### 4.3 Observable IOCs & SIEM Detections
- `@PJL FSUPLOAD` or `@PJL FSDOWNLOAD` commands containing `../` traversal sequences on port `9100/tcp`.
- Modifications to `~/.ssh/authorized_keys` initiated by print-spooler service accounts.
- Unexpected `SCM_RIGHTS` ancillary data transfers across Unix sockets.

---

## 5. Conclusion

Paperwork shows how trusting legacy peripheral protocols directly on network interfaces and passing open file descriptors across weak local IPC boundaries bypasses standard POSIX user and permission separation.
