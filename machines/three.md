---
title: Three
subtitle: Virtual Host Discovery, Permissive S3 Buckets & Webroot Execution
difficulty: easy
tags: [cloud, s3, virtual-hosting, web]
date: 2026-10
---

# Three: Virtual Host Discovery, Permissive S3 Buckets & Webroot Execution

An infrastructure case study covering name-based virtual host enumeration leading to an unauthenticated S3-compatible object storage bucket mapped directly into an executable PHP web root.

---

## 1. Architectural Scope

Modern web architectures frequently decouple static media assets from dynamic application nodes using S3-compatible object stores (such as LocalStack or MinIO). When administrative interfaces neglect bucket ACL enforcement—and both dynamic web hosting and bucket storage share a writable web directory—object upload turns directly into remote code execution.

```
[HTTP Virtual Hosting Perimeter]
  Domain Contact Metadata -> S3 Subdomain Discovery
        │
        ▼ (Unauthenticated Read/Write Bucket ACL)
  Arbitrary Script Upload to Shared Web-Accessible Storage
        │
        ▼ (PHP Interpreter Execution on Primary VHost)
  Remote Command Execution Under Web Service Context
```

---

## 2. Technical Vulnerability Vectors & Methodology

### 2.1 Virtual Host Enumeration & Object Storage Mapping
When a single HTTP listener serves multiple domains strictly based on the `Host` request header, internal service endpoints remain hidden from raw IP browsing. Inspecting contact references reveals backend storage subdomains routing to an exposed S3 API endpoint.

### 2.2 Unauthenticated Bucket Policies & Shared Execution Roots
- **The Defect:** The exposed S3 bucket accepts arbitrary read and write operations (`s3:ListBucket`, `s3:PutObject`) without enforcing real cryptographic authentication checks on incoming signatures, AND objects uploaded to the bucket become directly accessible and executable by the primary PHP application server. Uploading a minimal server-side script yields immediate code execution.

---

## 3. Engineering & Defensive Mitigations

| Vulnerability Surface | Recommended Remediation |
| :--- | :--- |
| **Object Storage ACLs** | Enforce authenticated IAM policies (`Block Public Access`), explicitly deny unauthenticated `PutObject`/`ListBucket` permissions, and validate cryptographic request signatures strictly. |
| **Storage-to-Runtime Separation** | Never serve user-writable object buckets from executable application web roots; route static assets through isolated CDN origins with explicit `Content-Disposition` headers and script execution disabled. |

---

## 4. Blue Team Counterpart: Detection, Hardening & IOCs

### 4.1 MITRE ATT&CK Mapping
- **T1530** — Data from Cloud Storage Object (Unauthenticated S3 Bucket Write)
- **T1505.003** — Server Software Component: Web Shell

### 4.2 Concrete Engineering & Hardening Controls
- **S3 / Object Storage Lockdown:** Enable **Block Public Access** at account and bucket levels; remove anonymous `Principal: "*"` policies permitting `s3:ListBucket` or `s3:PutObject`.
- **Static vs. Dynamic Separation:** Never serve user-writable object-storage buckets directly from an executable PHP/application webroot.

### 4.3 Observable IOCs & SIEM Detections
- Unauthenticated `PutObject` API calls uploading `.php` or executable extensions to storage buckets.
- HTTP `GET` requests executing newly uploaded scripts with command parameters.

---

## 5. Conclusion

Three demonstrates a high-impact cloud misconfiguration pattern: weak S3 bucket access control becomes an immediate RCE boundary whenever uploaded files remain reachable inside an active server-side interpreter path.
