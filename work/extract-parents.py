#!/usr/bin/env python3
"""Extract trimmed parent-session files for the first-thought westi bundle.
Parents (nearest first): coordinator c02168b6 (which spawned the builder
24e8433f), then main 6abbe781 (which spawned c02168b6).
- c02168b6 file: session_header + the FIRST subagent.spawn call naming the
  builder + its output.
- 6abbe781 file: session_header + the person's opening prompt (Nov 22 ~03:40
  auto-submit order, seq 73510) + the spawn call that started c02168b6 + its
  output. The bundle requires the chain to reach a parent file that HAS an
  opening message from the person.
No user messages beyond the opening prompt; nothing secret rides along.
"""
import json

WORK = '/home/hatch/workspace/makefun/u-rusdyxbt-one-letter-coffee-or-tea-89877fa0-westi'
BUILDER = '6353d9f4-0889-4031-8b3f-67e0dc41a901'
COORD = '8bbfc787-3cce-4940-a9b4-b717a1da82c0'
MAIN = '/home/hatch/agents/agent-6abbe781-a3d2-4607-afc8-16cbcf31911e/sessions/6abbe781-a3d2-4607-afc8-16cbcf31911e.jsonl'
COORD_PATH = '/home/hatch/agents/agent-8bbfc787-3cce-4940-a9b4-b717a1da82c0/sessions/8bbfc787-3cce-4940-a9b4-b717a1da82c0.jsonl'


def load_header(path):
    with open(path) as f:
        return json.loads(f.readline())


def find_spawn(path, agent_id):
    """First (spawn call, output) pair whose output names agent_id."""
    prev_call = None
    with open(path) as f:
        next(f)
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get('type') != 'item':
                continue
            item = rec.get('item') or {}
            t = item.get('type')
            if t == 'function_call' and item.get('name') == 'subagent.spawn':
                prev_call = rec
            elif t == 'function_call_output':
                if agent_id in (item.get('output') or ''):
                    return (prev_call, rec)
    raise AssertionError(f'no spawn output naming {agent_id} in {path}')


# 1. coordinator trim
header = load_header(COORD_PATH)
call, out = find_spawn(COORD_PATH, BUILDER)
out_path = f'{WORK}/parent-4f519f44.jsonl'
with open(out_path, 'w') as f:
    f.write(json.dumps(header) + '\n')
    for rec in (call, out):
        if rec is not None:
            f.write(json.dumps(rec) + '\n')
print(f'{out_path}: wrote header + spawn call + output')

# 2. main-session trim with the opening prompt
header = load_header(MAIN)
opening = None
with open(MAIN) as f:
    next(f)
    for line in f:
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get('type') == 'item' and rec.get('seq') == 73510:
            opening = rec
            break
assert opening is not None, 'opening message seq 73510 not found'
print('opening text:', (opening['item'].get('text') or '')[:100])
call, out = find_spawn(MAIN, COORD)
out_path = f'{WORK}/parent-6abbe781.jsonl'
with open(out_path, 'w') as f:
    f.write(json.dumps(header) + '\n')
    f.write(json.dumps(opening) + '\n')
    for rec in (call, out):
        if rec is not None:
            f.write(json.dumps(rec) + '\n')
print(f'{out_path}: wrote header + opening + spawn call + output')
