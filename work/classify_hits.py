#!/usr/bin/env python3
"""Classify the 5 non-public exact-value hits from secret_scan.py WITHOUT
printing any secret value. For each hit: source label(s), value length, count,
whether the value is a fragment of a longer token in its source file, and the
surrounding context with the value masked as [MASKED]."""
import json, os, re

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
TARGETS = [
    os.path.join(WORKDIR, "work", "scan-extract", "context", "repo", "_parent-4", "AGENTS.md"),
    os.path.join(WORKDIR, "work", "scan-extract", "context", "user", "muse-app", "workspace", "system", "system_prompt.md"),
]
for path in TARGETS:
    text = open(path, encoding="utf-8", errors="ignore").read()
    print(f"== {os.path.relpath(path, WORKDIR)}")
    for v, labs in sorted(vals.items(), key=lambda kv: -len(kv[0])):
        n = text.count(v)
        if not n:
            continue
        # is this value a fragment of a longer token in its source file?
        frag_info = []
        for lab in sorted(labs):
            src = dict(SECRET_FILES)[lab.split(':')[0]] if ':' not in lab else None
            srcpath = next((p for l, p in SECRET_FILES if l == lab), None)
            if srcpath and os.path.exists(srcpath):
                raw = open(srcpath, "rb").read().decode("utf-8", "ignore")
                # longest token run in the source containing v
                longest = 0
                for m in re.finditer(r"[A-Za-z0-9_\-+/=]+", raw):
                    if v in m.group(0):
                        longest = max(longest, len(m.group(0)))
                frag_info.append(f"{lab}: longest-containing-token={longest}")
        print(f"  len={len(v)} count={n} labels={','.join(sorted(labs))} | {'; '.join(frag_info)}")
        # masked context of first occurrence only
        i = text.find(v)
        ctx = text[max(0, i-60):i] + "[MASKED]" + text[i+len(v):i+len(v)+60]
        print(f"    context: {ctx!r}")
print("classification done — no secret values printed")
