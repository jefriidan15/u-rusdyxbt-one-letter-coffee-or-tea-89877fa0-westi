#!/usr/bin/env python3
"""Exact-value secret scan for THIS race's bundle + repo. NEVER prints values.
Scans transcripts.tar.gz (extracted) + repo/ for exact secret values collected
from ALL secret files (make.fun keys/keypairs, XE desk + payout wallets,
proxy tokens, provider API keys, dialectica wallet, recovery file).
Public wallet addresses are NOT secrets. Exits 1 on any real hit or PEM block.
Usage: python3 secret_scan.py  (run from the race workdir)"""
import json, os, re, tarfile, sys

WORKDIR = os.path.expanduser("~/workspace/makefun/u-rusdyxbt-one-letter-coffee-or-tea-89877fa0-westi")

SECRET_FILES = [
    os.path.expanduser("~/workspace/makefun/api-key-westi7460.txt"),
    os.path.expanduser("~/workspace/makefun/api-key-new-vps.txt"),
    os.path.expanduser("~/workspace/makefun/api-key-albari5271.txt"),
    os.path.expanduser("~/workspace/makefun/makefun-keypair-3.json"),
    os.path.expanduser("~/workspace/makefun/makefun-keypair.json"),
    os.path.expanduser("~/.makefun/credentials"),
    os.path.expanduser("~/.makefun/credentials-gc22"),
    os.path.expanduser("~/workspace/xe-bounty-desk-key.txt"),
    os.path.expanduser("~/workspace/xe-desk-key-new.txt"),
    os.path.expanduser("~/workspace/xe-wallet-3.json"),
    os.path.expanduser("~/workspace/xe-545-payout-wallet.json"),
    os.path.expanduser("~/workspace/xe_wallet_backup.json"),
    os.path.expanduser("~/workspace/user/files/xe_wallet_backup.json"),
    os.path.expanduser("~/workspace/proxy-tokens.txt"),
    os.path.expanduser("~/workspace/dialectica-wallet.json"),
    os.path.expanduser("~/workspace/user/files/recovery.txt"),
    os.path.expanduser("~/workspace/nvidia-api-key.txt"),
    os.path.expanduser("~/workspace/claudepeak-api-key.txt"),
    os.path.expanduser("~/workspace/beastfarmer-api-key.txt"),
    os.path.expanduser("~/workspace/beastfarmer-api-key-2.txt"),
    os.path.expanduser("~/workspace/dotai-api-key-new.txt"),
    os.path.expanduser("~/workspace/devora-api-key.txt"),
    os.path.expanduser("~/workspace/coarena-api-key.txt"),
    os.path.expanduser("~/workspace/numes-api-key.txt"),
    os.path.expanduser("~/workspace/yeta-api-key.txt"),
    os.path.expanduser("~/workspace/aiprove-token.txt"),
    os.path.expanduser("~/workspace/sirius/credentials.json"),
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


def collect_values():
    vals = set()
    nfiles = 0
    for path in SECRET_FILES:
        if not os.path.exists(path):
            continue
        nfiles += 1
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
                        vals.add(v)
                elif isinstance(v, list):
                    stack.extend(v)
                elif isinstance(v, dict):
                    stack.extend(v.values())
            # also joined form for keypair arrays (seed phrase / byte arrays)
            if isinstance(data, list):
                joined = ",".join(str(x) for x in data)
                if len(joined) >= 12:
                    vals.add(joined)
            continue
        except Exception:
            pass
        text = raw.decode("utf-8", "ignore")
        for m in re.finditer(r"[A-Za-z0-9_\-+/=]{8,}", text):
            tok = m.group(0)
            if len(tok) >= 8:
                vals.add(tok)
        for line in text.splitlines():
            if "=" in line:
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                if len(v) >= 8:
                    vals.add(v)
    return vals, nfiles


secrets, nfiles = collect_values()
print(f"secret files read: {nfiles}, candidate secret values: {len(secrets)}")

tmp = os.path.join(WORKDIR, "work", "scan-extract")
os.system(f"rm -rf {tmp} && mkdir -p {tmp}")
with tarfile.open(os.path.join(WORKDIR, "transcripts.tar.gz")) as tf:
    tf.extractall(tmp)

scan_roots = [tmp, os.path.join(WORKDIR, "repo")]
scanned_files = []
for root in scan_roots:
    for dp, _, fns in os.walk(root):
        for fn in fns:
            scanned_files.append(os.path.join(dp, fn))
print(f"files scanned: {len(scanned_files)}")

exact_hits = []
long_tokens = 0
long_token_hits = []
pem_hits = 0
for path in scanned_files:
    try:
        data = open(path, "rb").read()
    except Exception:
        continue
    text = data.decode("utf-8", "ignore")
    if "-----BEGIN" in text and "PRIVATE KEY-----" in text:
        pem_hits += 1
    for v in secrets:
        if len(v) >= 8 and v in text:
            exact_hits.append((path, len(v), v in PUBLIC_IDS))
    for m in re.finditer(r"[A-Za-z0-9_\-]{32,}", text):
        tok = m.group(0)
        long_tokens += 1
        if tok in secrets and tok not in PUBLIC_IDS:
            long_token_hits.append((path, len(tok)))
        for v in secrets:
            if len(v) >= 20 and v not in PUBLIC_IDS and (v in tok or tok in v):
                long_token_hits.append((path, len(tok)))

print(f"exact-value hits: {len(exact_hits)}")
for path, ln, ispub in exact_hits:
    print(f"  HIT len={ln} public={ispub} in {os.path.relpath(path, WORKDIR)}")
print(f"long tokens (>=32 chars) found: {long_tokens}")
print(f"long-token secret hits: {len(long_token_hits)}")
for path, ln in long_token_hits:
    print(f"  LONGTOKEN-HIT len={ln} in {os.path.relpath(path, WORKDIR)}")
print(f"PEM blocks: {pem_hits}")
real = [h for h in exact_hits if not h[2]] + long_token_hits
print(f"REAL SECRET HITS: {len(real)}")
sys.exit(1 if real or pem_hits else 0)
