# CertGuardian Threat Model

## Assets

Certificate inventory, ownership, historical evidence, expiry decisions, internal topology, and scanner availability.

## Threats and controls

| Threat | Control |
|---|---|
| SSRF or internal scanning through endpoint registration | Administrative-only writes, loopback binding, deployment egress allowlist |
| Forged or interception certificate | Platform CA validation, SNI, and hostname verification |
| Silent scan failure | Persist `ERROR` with bounded type/message and timestamp |
| Slow endpoint exhaustion | Bounded socket timeout and bounded scheduling inputs |
| Inventory or SQL injection | Typed validation and parameterized statements |
| Evidence tampering or theft | Filesystem least privilege, encrypted backups, external audit/retention controls |
| Misleading threshold configuration | Valid range, uniqueness, deterministic nearest-boundary classification |
| Stale alert state | Derive attention from latest immutable scan rather than a second mutable flag |
| Certificate replay/change unnoticed | SHA-256 leaf fingerprint, serial, issuer, SAN, and validity retained per scan |

## Residual risk

A trusted operator can intentionally scan sensitive destinations. System trust-store policy may differ from a client device. This reference does not inspect revocation, Certificate Transparency, every chain certificate, or national/internet-wide certificate data. One scanner and SQLite remain a single failure domain.
