# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.5.x   | :white_check_mark: |
| 2.4.x   | :white_check_mark: |
| < 2.4   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the repository maintainers at the email associated with the repository owner's GitHub account.

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the manifestation of the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Preferred Languages

We prefer all communications to be in English or Portuguese.

## Security Update Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine the affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release new security patch versions as soon as possible

## Security Best Practices

When using this application:

1. **Never commit sensitive credentials** - Use environment variables for API keys and secrets
2. **Keep dependencies updated** - Regularly update Python packages and review Dependabot alerts
3. **Use HTTPS** - Always deploy the application with HTTPS enabled
4. **Rate limiting** - The application includes Flask-Limiter for API rate limiting
5. **CORS configuration** - Review and restrict CORS settings for production environments
6. **Environment separation** - Use separate credentials for development, staging, and production

## Security Features

This project includes:

- CodeQL security analysis on every push and PR
- Dependabot for automated dependency updates
- Secret scanning (GitHub Advanced Security)
- Rate limiting on API endpoints
- CORS protection
- Input validation on API endpoints

## Disclosure Policy

When we learn of a security critical issue, we will:

1. Patch the vulnerability in a timely manner
2. Release a security advisory on GitHub
3. Credit the reporter (unless anonymity is requested)
