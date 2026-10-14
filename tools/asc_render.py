"""Render an LTspice .asc schematic to PNG/SVG using the real LTspice symbol graphics (.asy).
Symbols are looked up next to the .asc first, then in LTspice's library (%LOCALAPPDATA%/LTspice/lib/sym).
usage: python asc_render.py schematic.asc out.png [--svg] [--title "..."] [--no-directives]"""
import os, re, sys, math
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle

INK, WIRE, NAME, VAL, NET, DIRV, CMT, BG = '#1d1d1b', '#24479a', '#8a1c1c', '#24566e', '#1b7a3c', '#5b2b8c', '#6b6a66', '#ffffff'
SYMDIRS = []


def find_sym(name, here):
    cands = [here / f'{name}.asy'] + [d / f'{name}.asy' for d in SYMDIRS]
    for c in cands:
        if c.exists(): return c
    base = name.split('\\')[-1].split('/')[-1]
    for d in SYMDIRS:
        for p in d.rglob(f'{base}.asy'): return p
    return None


_cache = {}
def load_sym(name, here):
    if name in _cache: return _cache[name]
    p = find_sym(name, here)
    s = dict(lines=[], rects=[], circles=[], arcs=[], pins=[], windows={}, attrs={}, texts=[])
    if p is None:
        print('  missing symbol', name); s['rects'].append((0, 0, 32, 32)); _cache[name] = s; return s
    for ln in p.read_text(encoding='latin-1', errors='ignore').splitlines():
        t = ln.split()
        if not t: continue
        k = t[0]
        try:
            if k == 'LINE': s['lines'].append(tuple(map(int, t[2:6])))
            elif k == 'RECTANGLE': s['rects'].append(tuple(map(int, t[2:6])))
            elif k == 'CIRCLE': s['circles'].append(tuple(map(int, t[2:6])))
            elif k == 'ARC': s['arcs'].append(tuple(map(int, t[2:10])))
            elif k == 'PIN': s['pins'].append((int(t[1]), int(t[2])))
            elif k == 'WINDOW': s['windows'][int(t[1])] = (int(t[2]), int(t[3]), t[4])
            elif k == 'SYMATTR': s['attrs'][t[1]] = ' '.join(t[2:])
            elif k == 'TEXT': s['texts'].append((int(t[1]), int(t[2]), t[3], ' '.join(t[5:])))
        except (ValueError, IndexError):
            pass
    _cache[name] = s
    return s


def xf(rot):
    m = rot.startswith('M'); a = int(rot[1:])
    def f(x, y):
        if m: x = -x
        for _ in range(a // 90): x, y = -y, x
        return x, y
    return f


def render(asc, out, title=None, directives=True, svg=False):
    asc = Path(asc); here = asc.parent
    L = asc.read_text(encoding='latin-1', errors='ignore').splitlines()
    wires, flags, syms, texts = [], [], [], []
    cur = None
    for ln in L:
        t = ln.split()
        if not t: continue
        if t[0] == 'WIRE': wires.append(tuple(map(int, t[1:5])))
        elif t[0] == 'FLAG': flags.append((int(t[1]), int(t[2]), t[3]))
        elif t[0] == 'SYMBOL':
            cur = dict(name=t[1], x=int(t[2]), y=int(t[3]), rot=t[4], attrs={}, windows={}); syms.append(cur)
        elif t[0] == 'SYMATTR' and cur is not None: cur['attrs'][t[1]] = ' '.join(t[2:])
        elif t[0] == 'WINDOW' and cur is not None:
            cur['windows'][int(t[1])] = None if t[2:3] == ['Invisible'] or (len(t) > 4 and t[4] == 'Invisible') else (int(t[2]), int(t[3]), t[4])
        elif t[0] == 'TEXT':
            m = re.match(r'TEXT\s+(-?\d+)\s+(-?\d+)\s+(\S+)\s+(\d+)\s+(.*)$', ln)
            if m: texts.append((int(m[1]), int(m[2]), m[3], m[5]))
    pts = []
    for x1, y1, x2, y2 in wires: pts += [(x1, y1), (x2, y2)]
    for s in syms: pts.append((s['x'], s['y']))
    xs, ys = [p[0] for p in pts] + [t[0] for t in texts], [p[1] for p in pts] + [t[1] for t in texts]
    x0, x1, y0, y1 = min(xs) - 120, max(xs) + 220, min(ys) - 120, max(ys) + 120
    W, H = (x1 - x0), (y1 - y0)
    k = 0.0105                                                   # inches per LTspice unit
    fig = plt.figure(figsize=(W * k, H * k + (0.5 if title else 0)), dpi=150)
    ax = fig.add_axes([0, 0, 1, H / (H + (48 if title else 0))]); ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.axis('off')
    fig.patch.set_facecolor(BG)
    lw = 1.1; fs = 7.0
    for xa, ya, xb, yb in wires: ax.plot([xa, xb], [ya, yb], color=WIRE, lw=lw * 1.1, solid_capstyle='round', zorder=2)
    # junction dots: wire endpoints shared by >= 3 segment ends or a T onto a wire interior
    from collections import Counter
    ends = Counter()
    for xa, ya, xb, yb in wires: ends[(xa, ya)] += 1; ends[(xb, yb)] += 1
    pinpts = []
    for s in syms:
        sy = load_sym(s['name'], here); f = xf(s['rot'])
        for px, py in sy['pins']:
            dx, dy = f(px, py); pinpts.append((s['x'] + dx, s['y'] + dy))
    for p in pinpts: ends[p] += 1
    def on_interior(p):
        for xa, ya, xb, yb in wires:
            if (xa == xb == p[0] and min(ya, yb) < p[1] < max(ya, yb)) or (ya == yb == p[1] and min(xa, xb) < p[0] < max(xa, xb)): return True
        return False
    for p, n in ends.items():
        if n >= 3 or (n >= 1 and on_interior(p) and p in {(w[0], w[1]) for w in wires} | {(w[2], w[3]) for w in wires}):
            ax.add_patch(Circle(p, 4.5, color=WIRE, zorder=4))
    # symbols
    for s in syms:
        sy = load_sym(s['name'], here); f = xf(s['rot']); X, Y = s['x'], s['y']
        P = lambda a, b: (X + f(a, b)[0], Y + f(a, b)[1])
        for a, b, c, d in sy['lines']:
            p, q = P(a, b), P(c, d); ax.plot([p[0], q[0]], [p[1], q[1]], color=INK, lw=lw, solid_capstyle='round', zorder=3)
        for a, b, c, d in sy['rects']:
            cs = [P(a, b), P(c, b), P(c, d), P(a, d), P(a, b)]; ax.plot([q[0] for q in cs], [q[1] for q in cs], color=INK, lw=lw, zorder=3)
        for a, b, c, d in sy['circles']:
            cx, cy = P((a + c) / 2, (b + d) / 2); ax.add_patch(Circle((cx, cy), abs(c - a) / 2, fill=False, ec=INK, lw=lw, zorder=3))
        for a, b, c, d, e, g, h, i in sy['arcs']:
            cxs, cys = (a + c) / 2, (b + d) / 2; rx, ry = abs(c - a) / 2, abs(d - b) / 2
            th1 = math.degrees(math.atan2(-(g - cys), e - cxs)); th2 = math.degrees(math.atan2(-(i - cys), h - cxs))
            # LTspice arcs run counter-clockwise (screen) from (e,g) to (h,i); sample and transform
            if th2 <= th1: th2 += 360
            n = 24; pp = [P(cxs + rx * math.cos(math.radians(th1 + (th2 - th1) * j / n)), cys - ry * math.sin(math.radians(th1 + (th2 - th1) * j / n))) for j in range(n + 1)]
            ax.plot([q[0] for q in pp], [q[1] for q in pp], color=INK, lw=lw, zorder=3)
        for a, b, just, txt in sy['texts']:
            q = P(a, b); ax.text(q[0], q[1], txt, fontsize=fs, color=INK, ha='center', va='center', zorder=5)
        attrs = dict(sy['attrs']); attrs.update(s['attrs'])
        for idx, key, colr in ((0, 'InstName', NAME), (3, 'Value', VAL), (123, 'Value2', VAL), (39, 'SpiceLine', VAL)):
            w = s['windows'].get(idx, sy['windows'].get(idx)) if idx in s['windows'] else sy['windows'].get(idx)
            txt = attrs.get(key)
            if not txt or w is None: continue
            a, b, just = w; q = P(a, b)
            mirrored = s['rot'].startswith('M'); rot = s['rot'].lstrip('M'); va = 'center'
            ha = {'Left': 'left', 'Right': 'right', 'Center': 'center', 'Top': 'center', 'Bottom': 'center'}.get(just.lstrip('V'), 'left')
            if just.startswith('V') and rot in ('R90', 'R270'):
                # vertical-justified text on a quarter-turned symbol reads horizontally (LTspice convention)
                ha = 'center'; va = {('R90', 'VBottom'): 'bottom', ('R90', 'VTop'): 'top', ('R270', 'VTop'): 'bottom', ('R270', 'VBottom'): 'top'}[(rot, just)]
            elif rot in ('R90', 'R270') and ha != 'center':
                # horizontal text on a quarter-turned symbol: keep it horizontal, on the side the window points to
                ha = 'center'; va = 'bottom' if q[1] < Y else 'top'
            elif rot == 'R180' and ha != 'center':
                ha = 'right' if ha == 'left' else 'left'
            if mirrored and ha != 'center': ha = 'right' if ha == 'left' else 'left'
            ax.text(q[0], q[1], txt, fontsize=fs, color=colr, ha=ha, va=va, zorder=5, family='DejaVu Sans')
    # flags
    for x, y, n in flags:
        if n == '0':
            ax.plot([x - 16, x + 16, x, x - 16], [y, y, y + 16, y], color=INK, lw=lw, zorder=3)
        else:
            # place the label on the far side of the wire stub that reaches it
            d = None
            for xa, ya, xb, yb in wires:
                for (px, py), (ox, oy) in (((xa, ya), (xb, yb)), ((xb, yb), (xa, ya))):
                    if (px, py) == (x, y): d = (ox - x, oy - y)
            if d is None or (d[0] == 0 and d[1] > 0): kw = dict(x=x, y=y - 6, ha='center', va='bottom')
            elif d[0] == 0: kw = dict(x=x, y=y + 6, ha='center', va='top')
            elif d[0] > 0: kw = dict(x=x - 6, y=y, ha='right', va='center')
            else: kw = dict(x=x + 6, y=y, ha='left', va='center')
            ax.text(kw.pop('x'), kw.pop('y'), n, fontsize=fs * 1.05, color=NET, zorder=5, weight='bold', **kw)
            ax.add_patch(Circle((x, y), 2.5, color=NET, zorder=4))
    for x, y, just, txt in texts:
        if txt.startswith('!') and not directives: continue
        colr = DIRV if txt.startswith('!') else CMT
        body = txt[1:].replace('\\n', '\n')
        ha = 'left' if 'Left' in just else 'right' if 'Right' in just else 'center'
        ax.text(x, y, body, fontsize=fs * (0.95 if txt.startswith('!') else 1.0), color=colr, ha=ha, va='top', zorder=5,
                family='DejaVu Sans Mono' if txt.startswith('!') else 'DejaVu Sans', style='normal' if txt.startswith('!') else 'italic')
    if title:
        fig.text(0.01, 0.995, title, fontsize=13, color=INK, va='top', ha='left', weight='bold')
    fig.savefig(out, dpi=150, facecolor=BG)
    if svg: fig.savefig(str(Path(out).with_suffix('.svg')), facecolor=BG)
    plt.close(fig)
    print('wrote', out, f'({len(syms)} symbols, {len(wires)} wires)')


if __name__ == '__main__':
    a = sys.argv[1:]
    lib = Path(os.environ.get('LOCALAPPDATA', '')) / 'LTspice' / 'lib' / 'sym'
    SYMDIRS.append(lib)
    title = a[a.index('--title') + 1] if '--title' in a else None
    render(a[0], a[1], title=title, directives='--no-directives' not in a, svg='--svg' in a)
