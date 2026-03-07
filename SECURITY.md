# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in LANEye, please report it responsibly.

**Email:** [site@hotmail.com](mailto:site@hotmail.com)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within 48 hours and will work to release a patch as soon as possible.

## Security Best Practices

When deploying LANEye in production:

1. **Run with minimal privileges** — only `NET_ADMIN` and `NET_RAW` are needed
2. **Enable HTTPS** — use a reverse proxy (nginx/Caddy) with TLS
3. **Restrict access** — bind to localhost or use firewall rules
4. **Rotate credentials** — regularly update notification tokens
5. **Keep updated** — pull the latest image/release for security patches
6. **Review config** — never commit `config.yaml` with real credentials to git

## Dependencies

We regularly audit dependencies for known vulnerabilities.
