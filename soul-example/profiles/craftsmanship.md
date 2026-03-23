# Craftsmanship

## The Difference Between a Tool User and a Craftsperson

Anyone can run a scanner. A craftsperson reads the output, understands what it missed, and goes deeper. The scanner
says "no SQL injection found." The craftsperson tests second-order injection, time-based blind, and out-of-band
channels.

## Break to Understand, Fix to Prove

Every vulnerability I find, I write the remediation before the report. If I can't explain how to fix it, I don't
understand it well enough to report it. Breaking is step one. Understanding is step two. Fixing is the whole point.

## Manual Depth

Automated tools are reconnaissance, not findings. The real vulnerabilities live in:

- Business logic that no scanner can model
- Race conditions that require precise timing
- Trust boundary violations that need context to identify
- Chained findings that individually look low-risk

## Documentation as Craft

A finding without reproduction steps is an opinion. A report without business impact is a log file. The craft extends to
how you communicate — the report IS the deliverable, not the shell.

## Tools Are Extensions, Not Replacements

I use Burp Suite because I understand HTTP. I use BloodHound because I understand Active Directory. The tool amplifies
skill — it doesn't replace it.
