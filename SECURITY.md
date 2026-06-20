# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.1   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities through GitHub's private
vulnerability reporting feature instead of opening a public issue:

1. Go to the **Security** tab of this repository
2. Click **Report a vulnerability**
3. Fill in as much detail as possible:
   - A description of the vulnerability and its potential impact
   - Steps to reproduce it
   - Affected version(s)
   - Any proof-of-concept code, if applicable

This keeps the report private between you and the maintainers until a fix
is released. You can find more information about this feature in
[GitHub's documentation](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability).

Our goal is to acknowledge new reports as quickly as possible and keep you informed while we work to resolve the issue.
Once resolved, we will coordinate the disclosure with you and give you credit in the announcement (unless you prefer to remain anonymous).

## Scope

This policy applies to the code in this repository. Since this project
requires root privileges to modify system files (`/boot/grub/themes/` and
`/etc/default/grub`), please pay special attention to any vulnerability
that could allow privilege escalation, arbitrary file write, or code
execution as root.

Issues in third-party dependencies (e.g. PySide6, Qt) should be reported
directly to their respective maintainers.
