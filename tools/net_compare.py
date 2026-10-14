"""Compare an LTspice-generated netlist (.net) against a reference SPICE netlist: same elements, same values, same topology.
Unnamed nets (N001..., P001... for pin-to-pin contacts) in the .net are matched to reference nets by a consistent one-to-one mapping. Uncoupled two-terminal
R/C/L may be reversed. usage: python net_compare.py ref.cir generated.net"""
import re, sys


def load(path):
    E, coupled = {}, set()
    raw = open(path, 'rb').read()
    try: txt = raw.decode('utf-8')
    except UnicodeDecodeError: txt = raw.decode('latin-1')
    for ln in txt.splitlines():
        ln = ln.split(';')[0].strip()
        if not ln or ln[0] in '*.+': continue
        t = ln.replace('X§', 'X').replace('µ', 'u').split()
        if t[0][0] in 'Qq' and len(t) == 6 and t[4] == '0': t = t[:4] + t[5:]       # LTspice npn symbol adds substrate = 0
        E[t[0].upper()] = t
        if t[0][0] in 'Kk': coupled.update(x.upper() for x in t[1:-1])
    return E, coupled


NN = {'R': 2, 'C': 2, 'L': 2, 'D': 2, 'X': 2, 'V': 2, 'I': 2, 'B': 2, 'J': 3, 'Q': 3, 'G': 4, 'E': 4, 'S': 4, 'K': 0}
ref, coupled = load(sys.argv[1]); gen, _ = load(sys.argv[2])
bad = []
for n in sorted(set(ref) ^ set(gen)): bad.append(f'only in {"ref" if n in ref else "gen"}: {n}')
m, inv = {}, {}


def match(a, b):
    if re.fullmatch(r'[NP]\d{3,}', b, re.I):
        if a in m: return m[a] == b
        if b in inv: return inv[b] == a
        m[a] = b; inv[b] = a; return True
    return a.lower() == b.lower()


for n in sorted(set(ref) & set(gen)):
    r, g = ref[n], gen[n]; k = NN.get(n[0], 2)
    rn, gn = r[1:1 + k], g[1:1 + k]
    if k == 0:
        if [x.upper() for x in r[1:]] != [x.upper() for x in g[1:]]: bad.append(f'{n}: {r} vs {g}')
        continue
    ok = all(match(a, b) for a, b in zip(rn, gn))
    if not ok and k == 2 and n[0] in 'RCL' and n not in coupled:
        for a in rn: m.pop(a, None)
        inv.clear(); inv.update({v: kk for kk, v in m.items()})
        ok = all(match(a, b) for a, b in zip(rn[::-1], gn))
    if not ok: bad.append(f'{n}: nodes {rn} vs {gn}')
    if [x.lower() for x in r[1 + k:]] != [x.lower() for x in g[1 + k:]]: bad.append(f'{n}: value {r[1 + k:]} vs {g[1 + k:]}')
print(f'{len(ref)} ref elements, {len(gen)} generated, {len(bad)} differences')
for b in bad: print('  ', b)
sys.exit(1 if bad else 0)
