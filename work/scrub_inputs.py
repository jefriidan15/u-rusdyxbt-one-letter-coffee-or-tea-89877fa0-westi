#!/usr/bin/env python3
"""Scrub bundle INPUT files (copies only — never the harness originals).
Replaces every exact candidate secret value with [REDACTED-SECRET]
(longest first) and the literal PEM marker '-----BEGIN' with [REDACTED-PEM].
NEVER prints secret values — only source label, value length, count.
Public values (wallet addresses, make.fun domain) are NOT scrubbed.
Usage: python3 scrub_inputs.py"""
import json, os, re, sys

WORKDIR = os.path.expanduser("~/workspace/makefun/u-rusdyxbt-one-letter-coffee-or-tea-89877fa0-westi")

SECRET_FILES = [
    ("proxy-tokens", os.path.expanduser("~/workspace/proxy-tokens.txt")),
    ("api-westi", os.path.expanduser("~/workspace/makefun/api-key-westi7460.txt")),
    ("api-gc22", os.path.expanduser("~/workspace/makefun/api-key-new-vps.txt")),
    ("api-albari", os.path.expanduser("~/workspace/makefun/api-key-albari5271.txt")),
    ("kp3", os.path.expanduser("~/workspace/makefun/makefun-keypair-3.json")),
    ("kp1", os.path.expanduser("~/workspace/makefun/makefun-keypair.json")),
    ("creds", os.path.expanduser("~/.makefun/credentials")),
    ("creds-gc22", os.path.expanduser("~/.makefun/credentials-gc22")),
    ("xe-desk-557", os.path.expanduser("~/workspace/xe-bounty-desk-key.txt")),
    ("xe-desk-new", os.path.expanduser("~/workspace/xe-desk-key-new.txt")),
    ("xe-w3", os.path.expanduser("~/workspace/xe-wallet-3.json")),
    ("xe-545", os.path.expanduser("~/workspace/xe-545-payout-wallet.json")),
    ("xe-backup", os.path.expanduser("~/workspace/xe_wallet_backup.json")),
    ("xe-backup-user", os.path.expanduser("~/workspace/user/files/xe_wallet_backup.json")),
    ("dialectica-wallet", os.path.expanduser("~/workspace/dialectica-wallet.json")),
    ("recovery", os.path.expanduser("~/workspace/user/files/recovery.txt")),
    ("nvidia", os.path.expanduser("~/workspace/nvidia-api-key.txt")),
    ("claudepeak", os.path.expanduser("~/workspace/claudepeak-api-key.txt")),
    ("beastfarmer", os.path.expanduser("~/workspace/beastfarmer-api-key.txt")),
    ("beastfarmer-2", os.path.expanduser("~/workspace/beastfarmer-api-key-2.txt")),
    ("dotai-new", os.path.expanduser("~/workspace/dotai-api-key-new.txt")),
    ("devora", os.path.expanduser("~/workspace/devora-api-key.txt")),
    ("coarena", os.path.expanduser("~/workspace/coarena-api-key.txt")),
    ("numes", os.path.expanduser("~/workspace/numes-api-key.txt")),
    ("yeta", os.path.expanduser("~/workspace/yeta-api-key.txt")),
    ("aiprove", os.path.expanduser("~/workspace/aiprove-token.txt")),
    ("sirius", os.path.expanduser("~/workspace/sirius/credentials.json")),
]
PUBLIC_IDS = {
    "5Cp6PTGTvV9VEeboGeMY8aQsj5kSL1mFCGQu3Tk6BcAV",
    "JR782RiBv2bdGFHuUzwhjPuWHxsURxcPVezBQyTR91H",
    "01a1e5a4-bb10-768f-9670-0842d96b3366",
    "FvNKTvbQeT9QH2HHVjAfBjzdo3Wwg5svVgbKF7FvG8DZ",
    "7pzRpbycdbBsH6J44qMgiGGPHkww31z8eB6KNqmZfskA",
    "GaTfqiY7TuanXSFhLsnMUiZaparzViyYDN89ANN9Hwm1",
    "FAr1ztSTRUMBmv7F3ER9WKseqqvY9Fjnn6UFNQAPGYGj",
    "https://make.fun",
}


def collect():
    vals = {}
    for label, path in SECRET_FILES:
        if not os.path.exists(path):
            continue
        try:
            raw = open(path, "rb").read()
        except Exception:
            continue
        try:
            data = json.loads(raw)
            stack = [data]
            while stack:
                v = stack.pop()
                if isinstance(v, str):
                    if len(v) >= 8:
                        vals.setdefault(v, set()).add(label)
                elif isinstance(v, list):
                    stack.extend(v)
                elif isinstance(v, dict):
                    stack.extend(v.values())
            if isinstance(data, list):
                joined = ",".join(str(x) for x in data)
                if len(joined) >= 12:
                    vals.setdefault(joined, set()).add(label + ":joined")
            continue
        except Exception:
            pass
        text = raw.decode("utf-8", "ignore")
        for m in re.finditer(r"[A-Za-z0-9_\-+/=]{8,}", text):
            tok = m.group(0)
            if len(tok) >= 8:
                vals.setdefault(tok, set()).add(label)
        for line in text.splitlines():
            if "=" in line:
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 8:
                    vals.setdefault(v, set()).add(label)
    return {v: labs for v, labs in vals.items() if v not in PUBLIC_IDS}


vals = collect()
secrets = sorted(vals, key=len, reverse=True)
print(f"scrub candidates (non-public): {len(secrets)}")

JOBS = [
    ("/home/hatch/agents/agent-6353d9f4-0889-4031-8b3f-67e0dc41a901/sessions/6353d9f4-0889-4031-8b3f-67e0dc41a901.jsonl",
     os.path.join(WORKDIR, "work", "builder-session-scrubbed.jsonl")),
    (os.path.join(WORKDIR, "parent-4f519f44.jsonl"),
     os.path.join(WORKDIR, "work", "parent-4f519f44-scrubbed.jsonl")),
    (os.path.join(WORKDIR, "parent-6abbe781.jsonl"),
     os.path.join(WORKDIR, "work", "parent-6abbe781-scrubbed.jsonl")),
    (os.path.expanduser("~/workspace/system/system_prompt.md"),
     os.path.join(WORKDIR, "work", "system_prompt-scrubbed.md")),
    (os.path.expanduser("~/AGENTS.md"),
     os.path.join(WORKDIR, "work", "AGENTS-scrubbed.md")),
]

for src, dst in JOBS:
    content = open(src, encoding="utf-8", errors="ignore").read()
    total = 0
    for v in secrets:
        n = content.count(v)
        if n:
            content = content.replace(v, "[REDACTED-SECRET]")
            total += n
            print(f"  {os.path.basename(dst)}: scrubbed labels={','.join(sorted(vals[v]))} len={len(v)} count={n}")
    pem_n = content.count("-----BEGIN")
    if pem_n:
        content = content.replace("-----BEGIN", "[REDACTED-PEM]")
        print(f"  {os.path.basename(dst)}: scrubbed PEM markers count={pem_n}")
        total += pem_n
    open(dst, "w", encoding="utf-8").write(content)
    print(f"  {os.path.basename(dst)}: total replacements={total}")
print("scrub done")
