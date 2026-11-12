---
title: Bedside
subtitle: Unsafe Model Deserialization & Internal Service Traversal
difficulty: medium
tags: [deserialization, path-traversal, containers, linux]
date: 2026-11
---

# Bedside: Unsafe Model Deserialization & Internal Service Traversal

An architectural analysis of insecure binary deserialization across document-processing and machine-learning pipelines combined with containerized service traversal boundaries.

---

## 1. Architectural Scope

Clinical imaging and research platforms frequently decouple user-facing upload portals from internal medical imaging viewers and offline training pipelines. When serialized binary formats are trusted across container boundaries, low-privilege file processing bugs escalate into host-level compromise.

```
[Web Upload Surface]
  Research Artifact Ingestion (Containerized Worker)
        │
        ▼ (Unrestricted Binary Deserialization)
  Container Execution Context & Internal Mesh Pivot
        │
        ▼ (Unsanitized File Path Resolution)
  Internal Imaging Viewer Key Disclosure
        │
        ▼ (Unverified ML Checkpoint Deserialization)
  Host Root Privilege Escalation
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Untrusted Deserialization in Document Ingestion
Ingestion endpoints accepting archive or document artifacts for asynchronous research indexing must validate file types structurally rather than relying on extension or wrapper trust.
- **The Defect:** Passing user-controlled serialized byte streams into unsafe Python object deserializers inside a web worker allows arbitrary code execution during parsing, establishing an initial execution context within the container namespace.

### 2.2 Container-to-Service Path Traversal
Internal microservices exposed strictly to sister containers or semi-trusted network segments often omit canonical path validation.
- **The Defect:** A medical imaging web viewer resolves resource paths using raw user-supplied relative segments without enforcing base-directory jail checks (`realpath` prefix verification). From inside the compromised container bridge, traversing directory boundaries exposes sensitive private key material residing on the adjacent filesystem.

### 2.3 Unsafe Machine Learning Model Loading in Privileged Scripts
Administrative utilities invoking machine-learning frameworks frequently inherit insecure defaults designed for convenience over isolation.
- **The Defect:** Delegated administrative execution of model-validation scripts loads untrusted checkpoint artifacts using legacy serialization modes that permit embedded object reconstruction (`Pickle`-backed weights without restricted unpicklers). Any user able to supply or select a candidate checkpoint path achieves arbitrary code execution under the elevated context.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Artifact Ingestion** | Replace Pickle-based serialization with schema-validated structured formats (JSON, Safetensors) and sandbox parser workers. |
| **Internal Web File Serving** | Canonicalize requested paths server-side and reject any resolved target outside the intended media root directory. |
| **Model Checkpoint Loading** | Enforce strict safe-loading modes (`weights_only` with restricted globals) or adopt non-executable tensor formats such as `.safetensors`. |
| **Credential Separation** | Isolate SSH keys and host-access credentials from containerized service volumes; enforce network segmentation between microservices. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1190** — Exploit Public-Facing Application (Insecure Deserialization `CVE-2025-64512`)
- **T1059.006** — Command and Scripting Interpreter: Python

### 4.2 Concrete Engineering & Hardening Controls
- **Eliminate Unsafe Deserialization:** Upgrade the PDF parsing library beyond `CVE-2025-64512`; ban `pickle.loads()`, `cPickle`, and `yaml.load()` on untrusted inputs, replacing them with JSON or schema-validated data formats.
- **CI/CD Static Guardrails (SAST):** Fail builds when deserialization primitives (`pickle`, `marshal`, `shelve`) appear in request-handling code paths.
- **Document Processing Sandbox:** Execute file parsers inside ephemeral, network-isolated containers (`--network=none`, `read_only: true`, non-root UID, `cap_drop: ["ALL"]`).

### 4.3 Observable IOCs & SIEM Detections
- Uploaded PDF payloads triggering `pickle` / `UnpicklingError` exceptions in application logs.
- `auditd` / `Falco` alerts for `execve` spawning `/bin/sh`, `bash`, `curl`, or `nc` with a Python parser worker as parent process.

---

## 5. Conclusion

The Bedside architecture highlights how stacking unsafe deserialization primitives across separate application tiers—first in web ingestion, then in elevated ML validation tooling—turns isolated data-processing weaknesses into full host compromise.
