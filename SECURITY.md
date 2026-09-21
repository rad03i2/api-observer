# Security Policy

## Supported version
The latest release on `main` is supported.

## Security model
API Observer runs locally and sends only the HTTP requests explicitly configured by the operator. History is stored in a local SQLite database. Configuration files can contain HTTP headers and request bodies, so treat configurations containing credentials as secrets and never commit them.

The monitor accepts arbitrary HTTP/HTTPS targets by design. Do not run untrusted configuration files on networks where requests to internal services could be sensitive. Response bodies are capped at 1 MB by default and are not persisted; only status, latency, URL, check name, result, and message are stored.

## Reporting
Please report security issues privately to the repository owner through GitHub's supported private reporting channel when available. Do not publish credentials, tokens, private URLs, or exploit details in a public issue.
