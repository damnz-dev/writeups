---
title: Oraculo
subtitle: Indirect RAG Prompt Injection, Loopback Resolver Abuse & Unsigned Plugins
difficulty: medium
tags: [ai-security, rag, idor, linux]
date: 2026-11
---

# Oraculo: Indirect RAG Prompt Injection, Loopback Resolver Abuse & Unsigned Plugins

An assessment of an agentic LLM customer-support architecture examining security blind spots across Retrieval-Augmented Generation (RAG) boundaries, internal tool resolvers, API authorization, and automated plugin loaders.

---

## 1. Architectural Scope

Modern enterprise AI deployments integrate conversational agents with internal ticketing databases via RAG indices and structured tool-calling parsers. Filtering only direct user prompts while blindly trusting retrieved knowledge-base content creates an indirect execution bridge into loopback APIs.

```
[Public Support Ticketing & AI Staging Portal]
  Indirect Prompt Injection Embedded in Indexed Ticket Data
        │
        ▼ (RAG Context Assembly Bypassing Input Filters)
  Forced Tool-Call Invocation -> Insecure Loopback Endpoint Mapping
        │
        ▼ (Internal Service Token Reflection + Sequential Ticket IDOR)
  Developer SSH Private Key Disclosure
        │
        ▼ (Manifest Plugin Loader Without Cryptographic Hash Verification)
  Systemd Timer Module Load -> Host Root Execution
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Indirect Prompt Injection Across RAG Boundaries
While an anti-jailbreak filter inspects direct user chat messages for adversarial phrasing, it omits validation over documents retrieved dynamically from the ticket store.
- **The Defect:** Because the downstream tool-calling parser evaluates the fully assembled context window (system prompt + retrieved RAG documents + user query), tool-invocation delimiters embedded inside public support tickets execute authoritatively whenever those tickets match semantic retrieval queries.

### 2.2 Insecure Internal Endpoint Mapping & Service Token Leakage
Constrained agent tools accept high-level record categories rather than arbitrary URLs, relying on an internal routing map to translate logical names into loopback API routes.
- **The Defect:** Unprotected diagnostic mappings expose internal debugging routes blocked at the reverse proxy layer, causing the agent to reflect a privileged inter-service authentication token directly into chat responses.

### 2.3 API IDOR & Unsigned Automated Plugin Loading
Replaying the leaked service header against ticket APIs bypasses external access controls and exposes sensitive IT handoff records via sequential object enumeration, yielding developer SSH access.
- **The Defect:** Elevated automation runs a privileged plugin reloader on a periodic systemd timer that checks only whether manifest-listed Python files exist in a developer-writable directory—performing zero cryptographic integrity verification prior to dynamic module import.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **RAG & Agent Trust Boundaries** | Isolate untrusted retrieved data using structured escaping/delimiters, apply tool-call policy authorization independent of prompt text, and ban debug routes from tool resolvers. |
| **API Authorization** | Require per-ticket ownership or RBAC validation alongside service tokens and redact secret values from all debugging endpoints. |
| **Plugin Integrity** | Move plugin directories under strict root ownership (`0755`), implement SHA-256 or GPG signature verification before `importlib` execution, and drop unnecessary timer privileges. |

---

## 4. Conclusion

Oraculo highlights a core truth of AI application security: defensive filters placed solely in front of direct user input collapse when untrusted external records enter the same trusted prompt assembly pipeline and trigger backend tools lacking strict authorization and code-signing guarantees.
