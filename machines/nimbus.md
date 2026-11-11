---
title: Nimbus
subtitle: SSRF Metadata Bypass, Async Queue RCE & Build Container Escape
difficulty: hard
tags: [cloud, ssrf, deserialization, containers]
date: 2026-11
---

# Nimbus: SSRF Metadata Bypass, Async Queue RCE & Build Container Escape

A cloud-emulated security assessment analyzing SSRF parser discrepancies against instance metadata endpoints, unsafe message-queue deserialization, and privileged CI build container escapes.

---

## 1. Architectural Scope

Cloud-native platforms built around LocalStack-style AWS orchestration emulate IAM metadata endpoints, SQS asynchronous queues, and containerized build pipelines. Subtle normalization mismatches and insecure worker trust models create a direct chain from edge SSRF to underlying host escape.

```
[Web Application Edge]
  Alternative IP Representation Bypassing SSRF Denylist
        │
        ▼ (Cloud Metadata Service Exposure)
  Temporary IAM Session Credentials -> SQS Queue Access
        │
        ▼ (Unsafe YAML Deserialization in Queue Worker)
  Worker Execution inside Privileged Container Environment
        │
        ▼ (Environment Function Injection & Host Block Device Access)
  Host Filesystem Mount Escape -> Root Compromise
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 SSRF Validation Bypass via Alternative IP Encoding
URL fetchers frequently enforce naive regular-expression or dotted-quad denylists to block access to link-local metadata addresses.
- **The Defect:** Submitting alternative numeric representations (such as unsigned 32-bit decimal IPv4 notation) passes application string checks while lower-level HTTP networking libraries resolve the address directly to the cloud metadata endpoint, disclosing scoped IAM credentials.

### 2.2 Insecure Deserialization in Asynchronous Workers
Scoped queue permissions obtained via metadata credentials permit publishing messages onto internal SQS worker queues.
- **The Defect:** Backend Python consumers invoke permissive YAML deserialization (`yaml.load` with unsafe loaders) directly on queue message bodies, allowing object construction tags inside asynchronous jobs to execute arbitrary commands within the worker runtime.

### 2.3 Privileged Build Pipeline Escape
Compromised build runners operate inside containers granted excessive Linux capabilities or privileged host device visibility for CI operations.
- **The Defect:** Injecting crafted environment variables into automated build specifications hijacks shell function expansion inside privileged build execution, allowing access to host block devices and mounting the underlying host root filesystem.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **SSRF Protection** | Resolve hostnames to canonical IP structures before filtering, block link-local ranges at the network layer, and enforce IMDSv2 session tokens. |
| **Queue Consumer Parsing** | Strictly enforce `yaml.safe_load` or structured JSON schemas with message-origin signing for asynchronous queues. |
| **CI Build Isolation** | Run build workloads in rootless, unprivileged containers without `--privileged`, host block-device mapping, or Docker socket exposure. |

---

## 4. Conclusion

Nimbus illustrates common architectural pitfalls in emulated and real cloud deployments: parser mismatches nullify string-based SSRF defenses, unsafe deserializers turn message queues into execution sinks, and privileged build containers erase container-to-host boundaries.
