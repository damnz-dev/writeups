<p align="center">
  <img src="./assets/header.svg" width="900" alt="DAMNZ — Case Files"/>
</p>

<!-- STATS:START -->
<p align="center">
  <img src="https://img.shields.io/badge/case_files-8-5eead4?style=for-the-badge&labelColor=0b1117" alt="total"/>
  <img src="https://img.shields.io/badge/Machines-8-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/>
</p>
<!-- STATS:END -->

<p align="center"><sub>
Sanitized case studies from offensive security labs and CTFs. Each file documents <b>architecture, protocol behavior and mitigations</b>,
never flags, credentials, target addresses or copy-paste exploitation steps.
</sub></p>

---

### `$ ls -t case-files/`

<!-- INDEX:START -->
| # | Case | Category | Difficulty | Tags | Link |
|:-:|:-----|:--------:|:----------:|:-----|:----:|
| `08` | **Oraculo**<br><sub>Indirect RAG Prompt Injection, Loopback Resolver Abuse & Unsigned Plugins</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Medium-f59e0b?style=flat-square&labelColor=0b1117" alt="medium"/> | `ai-security` `rag` `idor` `linux` | [`↗ read`](./machines/oraculo.md) |
| `07` | **Nimbus**<br><sub>SSRF Metadata Bypass, Async Queue RCE & Build Container Escape</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Hard-ef4444?style=flat-square&labelColor=0b1117" alt="hard"/> | `cloud` `ssrf` `deserialization` `containers` | [`↗ read`](./machines/nimbus.md) |
| `06` | **Enigma**<br><sub>NFS/Mail Exposure, Authenticated CMS RCE & Loopback Console Injection</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Easy-22c55e?style=flat-square&labelColor=0b1117" alt="easy"/> | `nfs` `cms` `command-injection` `linux` | [`↗ read`](./machines/enigma.md) |
| `05` | **DutyBound**<br><sub>Barcode Audit Injection, X11 Socket Hijacking & Systemd Path Eval</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Medium-f59e0b?style=flat-square&labelColor=0b1117" alt="medium"/> | `sqli` `x11` `systemd` `linux` | [`↗ read`](./machines/dutybound.md) |
| `04` | **DarkZeroReturns**<br><sub>CI/CD Runner Abuse, Kerberos Collision & Cross-Forest Trust Forgery</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Hard-ef4444?style=flat-square&labelColor=0b1117" alt="hard"/> | `active-directory` `cross-forest` `kerberos` `cicd` | [`↗ read`](./machines/darkzeroreturns.md) |
| `03` | **Cap**<br><sub>Authorization Gaps in Telemetry Capture & POSIX Capabilities</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Easy-22c55e?style=flat-square&labelColor=0b1117" alt="easy"/> | `idor` `pcap` `capabilities` `linux` | [`↗ read`](./machines/cap.md) |
| `02` | **Bedside**<br><sub>Unsafe Model Deserialization & Internal Service Traversal</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Medium-f59e0b?style=flat-square&labelColor=0b1117" alt="medium"/> | `deserialization` `path-traversal` `containers` `linux` | [`↗ read`](./machines/bedside.md) |
| `01` | **Autopilot**<br><sub>Protocol Breakdown & Hybrid Cross-Relay Analysis</sub> | <img src="https://img.shields.io/badge/Machines-5eead4?style=flat-square&labelColor=0b1117" alt="Machines"/> | <img src="https://img.shields.io/badge/Insane-a855f7?style=flat-square&labelColor=0b1117" alt="insane"/> | `active-directory` `linux` `ntlm-relay` `webdav` | [`↗ read`](./machines/autopilot.md) |
<!-- INDEX:END -->

<sub>This table, the category pages and <code>index.json</code> are rebuilt automatically by GitHub Actions; don't edit them by hand.</sub>

---

### `$ tree -L 1`

```text
writeups/
├── machines/    full-chain lab machines (AD · Linux · hybrid)
├── web/         web application challenges
├── pwn/         binary exploitation
├── crypto/      cryptography
├── rev/         reverse engineering
├── forensics/   forensics & incident artifacts
├── misc/        everything else
├── TEMPLATE.md  skeleton for new case files
└── scripts/     index generator (run by CI)
```

### `$ cat HOWTO`

1. Copy [`TEMPLATE.md`](./TEMPLATE.md) into the right folder as `case-name.md`.
2. Fill in the header block (`title`, `subtitle`, `difficulty`, `tags`, `date`) and write the case.
3. Commit. The index, badges and category pages update themselves.

<p align="center"><sub><code>// read the architecture, not the answer key</code></sub></p>
