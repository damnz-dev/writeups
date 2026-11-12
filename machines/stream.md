---
title: Stream
subtitle: Actuator Heapdump Secrets, Async Kafka XXE & Process Argument Races
difficulty: medium
tags: [spring-boot, xxe, kafka, clickhouse]
date: 2026-10
---

# Stream: Actuator Heapdump Secrets, Async Kafka XXE & Process Argument Races

An architectural assessment of an event-streaming telemetry stack combining Spring Boot gateway exposure, asynchronous XML external entity expansion across Kafka pipelines, `procfs` credential leakage, and ClickHouse file-engine abuse.

---

## 1. Architectural Scope

Event-driven telemetry architectures frequently chain lightweight HTTP ingestion proxies, Kafka message brokers, asynchronous XML consumers, and analytical databases such as ClickHouse. When unauthenticated JVM diagnostics leak database secrets and downstream XML consumers parse untrusted payloads asynchronously, in-band exfiltration completes entirely within analytical tables.

```
[API Gateway Perimeter]
  Exposed JVM Diagnostics Endpoint (Heapdump)
        │
        ▼ (In-Memory DataSource Secret Recovery)
  Read Access to Analytical Event Store (ClickHouse)
        │
        ▼ (Async XML Consumer XXE Over Kafka Queue)
  In-Band File Disclosure Stored Inside Materialized Columns
        │
        ▼ (Broker SASL Credentials -> Host Access -> procfs Timing Leak)
  Analytical DB Admin Secret -> File-Function Overwrite of Scheduled Root Task
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Unauthenticated JVM Heapdump Exposure
Spring Boot Actuator configurations restricting `env` endpoints often overlook `heapdump`, assuming binary memory dumps are impractical to exploit.
- **The Defect:** Active memory snapshots retain plain JDBC and analytical datastore connection pool credentials in string tables, granting immediate read access to backend telemetry warehouses.

### 2.2 Asynchronous In-Band XXE Across Message Brokers
The public HTTP XML ingestion service validates message framing superficially using string checks before publishing raw bodies to Kafka—bypassing egress firewall rules because no outbound connections occur during parsing.
- **The Defect:** A downstream asynchronous consumer parses queued XML with external entities enabled (`file://`) and persists parsed fields into ClickHouse tables already readable using credentials from the heapdump. Inspecting materialized rows leaks Kafka broker configuration secrets and grants SSH access into the infrastructure host.

### 2.3 `procfs` Command-Line Leakage & Analytical File-Engine Overwrite
Periodic root-owned dead-letter-queue draining tasks invoke database CLI clients while passing sensitive administrative passwords directly via command-line arguments.
- **The Defect:** Because default `procfs` visibility exposes `/proc/<pid>/cmdline` globally for transient execution windows, unprivileged local users observe the administrative database password cleanly. High-privilege ClickHouse accounts lacking filesystem/function sandboxing can subsequently write arbitrary files via table functions (`file()`) to overwrite scheduled scripts invoked by systemd timers.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Spring Boot Actuators** | Disable `heapdump` in production profiles (`management.endpoints.web.exposure.exclude`), or enforce mutual TLS and administrative RBAC strictly. |
| **XML Broker Consumers** | Disable DTDs and external entity resolution completely inside downstream XML parsers regardless of internal network isolation. |
| **Secret Passing & `procfs`** | Pass database credentials exclusively via protected files or environment variables rather than CLI arguments; mount `/proc` with `hidepid=2` and restrict analytical DB `file()` / `INTO OUTFILE` capabilities. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1552** — Unsecured Credentials (Spring Boot Actuator Heapdump)
- **T1005** — Data from Local System (XXE In-Band)

### 4.2 Concrete Engineering & Hardening Controls
- **Spring Boot Actuator Lockdown:** Restrict exposed endpoints to `health,info` (`management.endpoints.web.exposure.include=health,info`); explicitly disable `heapdump` and `env` in production.
- **XXE Prevention:** Disable `DOCTYPE` declarations and external entities in XML parsers (`defusedxml` in Python, `FEATURE_DISALLOW_DOCTYPE_DECL = true` in Java).
- **Secret Management:** Avoid keeping long-lived ClickHouse credentials in plaintext JVM properties; use short-lived tokens or external secret vaults.

### 4.3 Observable IOCs & SIEM Detections
- HTTP requests targeting `/actuator/heapdump`, `/actuator/env`, or `/heapdump`.
- XML payloads containing `<!DOCTYPE` or `<!ENTITY ... SYSTEM "file://">`.
- ClickHouse authentications originating from unauthorized hosts or service accounts.

---

## 5. Conclusion

Stream illustrates why asynchronous message pipelines do not eliminate injection risks: when an unauthenticated heapdump supplies database read visibility, blind downstream XXE becomes trivial in-band data exfiltration—and transient CLI secrets on Linux dismantle host isolation.
