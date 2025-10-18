# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in LANEye, please report it by emailing:

**site@hotmail.com**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We take all security reports seriously and will respond within 48 hours.

## Security Best Practices

When deploying LANEye:

1. **Run with minimal privileges**: Use Docker with limited capabilities
2. **Secure your database**: Use strong passwords for PostgreSQL
3. **Enable authentication**: Add authentication middleware for production
4. **Use HTTPS**: Deploy behind a reverse proxy with SSL/TLS
5. **Keep updated**: Regularly update dependencies and Docker images
6. **Network isolation**: Run in isolated network segment
7. **Monitor logs**: Enable logging and monitor for suspicious activity

## Known Security Considerations

- LANEye requires `NET_ADMIN` and `NET_RAW` capabilities for packet capture
- Network scanning may trigger IDS/IPS systems - whitelist appropriately
- API endpoints should be protected with authentication in production
- WebSocket connections should use secure protocols (wss://)

## Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2).
