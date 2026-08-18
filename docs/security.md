# CertGuardian Security

- The scanner uses `ssl.create_default_context`, SNI, CA validation, and hostname verification. There is no insecure verification mode.
- Endpoint registration is administrative because it can be used for internal port access or metadata discovery. Bind locally or add authentication, authorization, rate limits, and egress allowlists.
- Ports, host lengths, intervals, threshold values, API history limits, and socket timeouts are bounded.
- SQL uses parameters; full scan evidence is JSON encoded; API conflict and missing-resource errors hide SQL details.
- The container runs as UID 10001 with a read-only root filesystem and `no-new-privileges`.
- Protect the database and backups: hostnames, ownership, failure time, SANs, issuers, serials, and fingerprints reveal infrastructure information.
- Do not store credentials in hostnames or use CertGuardian as an unauthenticated public scanning proxy.
