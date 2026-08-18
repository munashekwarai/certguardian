# CertGuardian

**Cybersecurity · PKI · DevOps**

## Problem
Certificate dependencies are tracked in spreadsheets, calendars, or memory.

## Who This Helps
Operators of websites, APIs, VPNs, proxies, and internal applications.

## Why It Matters
An unnoticed expiry can cause an outage, failed integration, and emergency renewal.

## Constraints
The system must be inexpensive, inspectable, testable without paid services, conservative about claims, and safe with untrusted input. SQLite/local execution is the default; production deployments need deliberate persistence, identity, networking, and backup choices.

## Solution
A TLS scanner validates hostnames, extracts issuer/SAN/validity, assigns threshold alerts, and stores scan history.

## Architecture
```mermaid
flowchart LR
  Input[Validated input] --> Core[Domain engine]
  Core --> Store[(Durable store)]
  CLI[CLI] --> Core
  API[REST API] --> Core
  Core --> Evidence[Results and evidence]
```
See [architecture](docs/architecture.md).

## Features
The repository implements its domain engine, validation, durable/local state where applicable, executable interfaces, meaningful tests, structured errors, and automation.

## Technology Stack
Python 3.11 provides a portable typed core; FastAPI provides OpenAPI-backed HTTP endpoints; Typer provides operator-friendly commands; SQLite provides a zero-service evidence store. CloudForge instead uses Terraform, Docker, NGINX, and shell-based verification.

## Setup
```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```
Copy `.env.example` to `.env` only for local overrides; `.env` is ignored.

## Usage
```bash
python -m app.cli --help
uvicorn app.api:app --host 127.0.0.1 --port 8000
```
CloudForge users should follow `docs/deployment.md`.

## Testing
```bash
pytest -q
```
Tests exercise domain behavior and failure paths without paid infrastructure.

## Security
Inputs are bounded and validated, secrets are accepted through the environment rather than source, errors avoid sensitive internals, and CI runs tests. See [security](docs/security.md) and [threat model](docs/threat-model.md).

## Limitations
It observes presented TLS certificates; it cannot renew certificates or discover unregistered endpoints.

## Contributing
Read [CONTRIBUTING.md](CONTRIBUTING.md), add tests for behavior changes, and avoid real personal or secret data in fixtures.
