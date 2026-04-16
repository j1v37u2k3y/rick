# Example CTF Challenge — Web Exploitation

**Event:** Example CTF 2026
**Category:** Web
**Points:** 250
**Difficulty:** Medium

## Description

Login portal with "super secure" authentication. Find the flag.

## Solution

Tested login form for SQL injection:

```
Username: ' OR 1=1 --
Password: anything
```

Bypassed authentication. Flag displayed on the dashboard.

**Flag:** `flag{sql_injection_is_not_dead_2026}`

## Techniques

- Manual SQL injection testing
- Authentication bypass via tautology injection
- No WAF or input sanitization present

## Tools Used

- Burp Suite (intercept and replay)
- Browser dev tools

## Takeaway

Classic SQLi still shows up in CTFs and in the wild. Always test auth forms manually before reaching for SQLMap.
