#!/usr/bin/env python3
# Arasaka watermark: emits ImageMagick MVG on stdout. Canvas 3840x2400.
# Usage: watermark.py <cjk-black.ttf> <cjk-regular.ttf> <mono-bold.ttf> "<logo bbox: x y w h>"
import math, random, sys
W, H = 3840, 2400
CJK, CJKR, MONO = sys.argv[1:4]
bx, by, bw, bh = [int(v) for v in sys.argv[4].split()]
RED, DARK, GREY, LIGHT, PEAK, INK = '#e10600', '#7a0008', '#9a9aa2', '#d8d8dc', '#ffb0a8', '#0a0a0c'
out = ["push graphic-context"]
def txt(x, y, s, size, col, font=MONO, a=1.0):
    out.append(f"stroke none fill '{col}' fill-opacity {a} font '{font}' font-size {size} text {x},{y} '{s}'")
def rect(x0, y0, x1, y1, col, a=1.0):
    out.append(f"stroke none fill '{col}' fill-opacity {a} rectangle {x0},{y0} {x1},{y1}")
def poly(pts, col=RED, w=3, a=0.9, close=False):
    kind = 'polygon' if close else 'polyline'
    out.append(f"stroke '{col}' stroke-width {w} stroke-opacity {a} fill-opacity 0 {kind} {' '.join(f'{x},{y}' for x, y in pts)}")
def via(x, y, a=0.9, r=11):
    out.append(f"stroke '{RED}' stroke-width 3 stroke-opacity {a} fill '{INK}' fill-opacity 0.9 circle {x},{y} {x + r},{y}")
def pad(x, y, a=0.9, s=11):
    rect(x - s, y - s, x + s, y + s, RED, a)
def chip(x0, y0, w, h, pins, pitch, label, sub, sides='lr', a=0.85, pin_len=22, pin_w=10):
    # IC footprint: dark body, red outline, pin-1 dot, pins on the given sides.
    # Returns the pin coordinates per side so traces can land on them.
    out.append(f"stroke '{RED}' stroke-width 2 stroke-opacity {a} fill '{INK}' fill-opacity 0.85 rectangle {x0},{y0} {x0 + w},{y0 + h}")
    out.append(f"stroke none fill '{RED}' fill-opacity {a} circle {x0 + 16},{y0 + 16} {x0 + 21},{y0 + 16}")
    ys = [y0 + h // 2 - (pins - 1) * pitch // 2 + i * pitch for i in range(pins)]
    xs = [x0 + w // 2 - (pins - 1) * pitch // 2 + i * pitch for i in range(pins)]
    res = {}
    if 'l' in sides:
        for y in ys: rect(x0 - pin_len, y - pin_w // 2, x0, y + pin_w // 2, RED, a)
        res['l'] = [(x0 - pin_len, y) for y in ys]
    if 'r' in sides:
        for y in ys: rect(x0 + w, y - pin_w // 2, x0 + w + pin_len, y + pin_w // 2, RED, a)
        res['r'] = [(x0 + w + pin_len, y) for y in ys]
    if 't' in sides:
        for x in xs: rect(x - pin_w // 2, y0 - pin_len, x + pin_w // 2, y0, RED, a)
        res['t'] = [(x, y0 - pin_len) for x in xs]
    if 'b' in sides:
        for x in xs: rect(x - pin_w // 2, y0 + h, x + pin_w // 2, y0 + h + pin_len, RED, a)
        res['b'] = [(x, y0 + h + pin_len) for x in xs]
    txt(x0 + w - 16 - 24 * len(label) * 0.6, y0 + 30, label, 24, RED, MONO, a)
    txt(x0 + 16, y0 + h - 18, sub, 20, GREY, MONO, 0.8)
    return res
def fid(x, y, label, a=0.6, r=24):
    # Fiducial: crosshair in a circle with a red center dot, like PCB alignment marks.
    out.append(f"stroke '{GREY}' stroke-width 2 stroke-opacity {a} fill-opacity 0 circle {x},{y} {x + r},{y}")
    poly([(x - r - 14, y), (x + r + 14, y)], col=GREY, w=2, a=a)
    poly([(x, y - r - 14), (x, y + r + 14)], col=GREY, w=2, a=a)
    out.append(f"stroke none fill '{RED}' fill-opacity {a + 0.2} circle {x},{y} {x + 6},{y}")
    txt(x + r + 22, y - r, label, 18, GREY, MONO, a)

# Panel geometry (right side)
PX0, PX1, PY0, PY1 = 3230, 3800, 430, 2220

# ---- Matrix columns (small, scattered, outside the reserved zones) ----
chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン荒坂企業警備銀行製造忠誠秩序権力監視0123456789"
random.seed(21)
cols = []
def clash(x, y0, y1, s):
    if x < 1600 and y1 > by - 120 and y0 < 2150: return True      # logo, texts, traces
    if x < 210: return True                                        # vertical text
    if x + s > PX0 - 60 and y1 > 250: return True                  # panel
    if x + s > 2900 and y0 < 480: return True                      # sys block + bus
    if x + s > 2840 and y1 > 1850: return True                     # bus E
    if x + s > 1560 and x < 1960 and y1 > 1900: return True        # chip U1
    if x + s > 2780 and x < 3240 and y1 > 900 and y0 < 1320: return True  # chip U2 + bus F
    if (x < 300 or x + s > 3560) and (y0 < 280 or y1 > 2160): return True  # fiducials
    return any(abs(cx - x) < (cs + s) * 1.4 and not (y1 < cy0 or y0 > cy1) for (cx, cy0, cy1, cs) in cols)
tries = 0
while len(cols) < 34 and tries < 8000:
    tries += 1
    s = random.choice([35, 40, 45, 50]); n = random.randint(6, 22)
    x = random.randint(220, W - s - 120); y0 = random.randint(80, H - 300); y1 = y0 + n * int(s * 1.15)
    if y1 > H - 60 or clash(x, y0, y1, s): continue
    cols.append((x, y0, y1, s))
    base = random.uniform(0.16, 0.48); col = RED if random.random() < 0.75 else LIGHT
    for k in range(n):
        txt(x, y0 + k * int(s * 1.15), random.choice(chars), s, col, CJKR, round(base * (0.5 + 0.5 * random.random()), 2))

# ---- Left vertical text + rail ----
for i, ch in enumerate("荒坂コーポレーション"):
    txt(60, 300 + i * 80, ch, 58, RED, CJK)
rect(74, 1140, 88, 2200, RED)

# ---- Logo, texts aligned on the kanji ink box ----
txt(300, 1560, '荒坂', 520, RED, CJK)
s1 = int(bw / (19 * 0.6)); s2 = int(bw / (36 * 0.6))
y1 = by + bh + 30 + s1; y2 = y1 + int(s2 * 1.5)
txt(bx, y1, 'ARASAKA CORPORATION', s1, LIGHT)
txt(bx, y2, 'SECURITY // BANKING // MANUFACTURING', s2, GREY)
txt(bx, y2 + 40, 'PCB REV 2.077  //  NIGHT CITY  //  J1', 22, GREY, MONO, 0.8)

# ---- PCB traces ----
d = 26  # trace pitch
# Bus A: 5 traces leaving the tagline to the right, 45deg down, into chip U1.
ya = y2 + 110; run = 140
U1X, U1W, U1H = bx + 1290, 230, 160
u1 = chip(U1X, ya + run - 28, U1W, U1H, 5, d, 'U1', 'SEC-CTRL 7A3F', 'lr')
for i in range(5):
    y = ya + i * d; xa = bx + 760 - i * d
    pts = [(bx, y), (xa, y), (xa + run, y + run), u1['l'][i]]
    poly(pts, a=0.85); via(pts[0][0], pts[0][1], 0.85)
for (x, y) in u1['r']:
    poly([(x, y), (x + 50, y)], a=0.85); pad(x + 58, y, 0.85, 8)
# Bus B: 3 traces from the left rail into the logo top edge, with vias.
for i in range(3):
    y = 1180 + i * d
    pts = [(88, y), (bx - 120 + i * d, y), (bx - 60 + i * d, y - 60), (bx - 60 + i * d, by - 40)]
    poly(pts, a=0.7, w=2); via(pts[-1][0], pts[-1][1], 0.7, 8)
# Bus C: marker line above the logo with pads, like a silkscreen ruler.
poly([(bx, by - 70), (bx + bw, by - 70)], a=0.6, w=2)
for k in range(9):
    x = bx + k * bw // 8
    rect(x - 2, by - 84, x + 2, by - 56, RED, 0.6)
# Bus D: 4 traces from the sys block underline down into the panel header.
for i in range(4):
    x = 3000 + i * d
    pts = [(x, 392), (x, 405 + i * 10), (x + 60 - i * 0, 465 + i * 10), (PX0 - 20 + i * 0, 465 + i * 10)]
    poly(pts, a=0.8, w=2); via(pts[0][0], pts[0][1], 0.8, 7)

# Bus E: 3 traces leaving the panel bottom-left, 45deg down-left to pads near the bottom edge.
for i in range(3):
    y = 1960 + i * d
    pts = [(PX0, y), (PX0 - 160 - i * d, y), (PX0 - 260 - i * d, y + 100), (PX0 - 260 - i * d, 2280 - i * 30)]
    poly(pts, a=0.75, w=2); pad(pts[-1][0], pts[-1][1], 0.75, 9)
# Bus F: 5 traces from chip U2 (QFP) straight into the panel's left edge.
U2X, U2Y, U2S = 2880, 990, 176
u2 = chip(U2X, U2Y, U2S, U2S, 5, d, 'U2', 'NET-LINK', 'lrtb')
for (x, y) in u2['r']:
    poly([(x, y), (PX0, y)], a=0.75, w=2); via(x + 60, y, 0.75, 7)
for (x, y) in u2['l']:
    poly([(x, y), (x - 40, y)], a=0.75, w=2); pad(x - 48, y, 0.75, 7)
for (x, y) in u2['t']:
    poly([(x, y), (x, y - 36)], a=0.75, w=2); pad(x, y - 44, 0.75, 7)
for (x, y) in u2['b']:
    poly([(x, y), (x, y + 36)], a=0.75, w=2); pad(x, y + 44, 0.75, 7)
txt(U2X + U2S + 40, U2Y - 60, 'BUS_F  x5', 20, GREY, MONO, 0.7)
# Fiducials in the four corners.
fid(150, 160, 'FID1'); fid(3690, 160, 'FID2'); fid(150, 2280, 'FID3'); fid(3690, 2280, 'FID4')
# Silkscreen labels on the buses.
txt(bx + 20, ya - 14, 'BUS_A  x5', 20, GREY, MONO, 0.7)
txt(110, 1160, 'J2', 20, GREY, MONO, 0.7)
txt(3000, 470 + 50, 'BUS_D', 20, GREY, MONO, 0.7)
txt(PX0 - 300, 1940, 'GND', 20, GREY, MONO, 0.7)

# ---- Sys block ----
txt(2980, 300, 'SYS.ACCESS  ::  LEVEL 07', 36, GREY)
txt(2980, 360, '認証済み', 40, RED, CJK)
rect(2980, 380, 3820, 392, RED)

# ---- Instrument panel ----
ch = 40  # chamfer
poly([(PX0, PY0), (PX1 - ch, PY0), (PX1, PY0 + ch), (PX1, PY1), (PX0 + ch, PY1), (PX0, PY1 - ch)], a=0.75, w=2, close=True)
# header bar with cut corner, black text on red
out.append(f"stroke none fill '{RED}' fill-opacity 0.95 polygon {PX0},{PY0} {PX1 - ch},{PY0} {PX1},{PY0 + ch} {PX1},{PY0 + 56} {PX0},{PY0 + 56}")
txt(PX0 + 18, PY0 + 40, 'ARASAKA // SYS.MONITOR', 28, INK)
txt(PX1 - 120, PY0 + 40, 'v2.077', 24, INK)
# gauges: tick scale (no numbers) + 4 framed bars with peak segment
GY0, GY1 = 560, 1500; seg_h, gap = 24, 7; nseg = (GY1 - GY0) // (seg_h + gap)
for k in range(5):
    y = GY0 + k * (GY1 - GY0) // 4
    poly([(PX0 + 30, y), (PX0 + 60, y)], col=GREY, w=2, a=0.7)
random.seed(3)
values = [87, 64, 93, 41]
for g in range(4):
    x = 3330 + g * 115; w = 80
    poly([(x - 8, GY0 - 10), (x + w + 8, GY0 - 10), (x + w + 8, GY1 + 10), (x - 8, GY1 + 10)], a=0.5, w=2, close=True)
    lit = int(nseg * values[g] / 100)
    for s_ in range(nseg):
        y = GY1 - (s_ + 1) * (seg_h + gap)
        if s_ < lit - 1: rect(x, y, x + w, y + seg_h, RED, 1.0)
        elif s_ == lit - 1: rect(x, y, x + w, y + seg_h, PEAK, 1.0)
        else: rect(x, y, x + w, y + seg_h, GREY, 0.18)

def area(pts, col, a):
    out.append(f"stroke none fill '{col}' fill-opacity {a} polygon {' '.join(f'{x},{y}' for x, y in pts)}")
def scope_frame(x0, y0, x1, y1, vstep=60, hstep=50):
    # Faint scope graticule inside a thin frame.
    for x in range(x0 + vstep, x1, vstep): poly([(x, y0), (x, y1)], col=GREY, w=1, a=0.14)
    for y in range(y0 + hstep, y1, hstep): poly([(x0, y), (x1, y)], col=GREY, w=1, a=0.14)
    poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], col=GREY, w=2, a=0.4, close=True)
SX0, SX1 = PX0 + 30, PX1 - 30

# Oscilloscope: three overlaid traces, carrier + slow wave + noise.
OY0, OY1 = 1550, 1760; mid = (OY0 + OY1) // 2
scope_frame(SX0, OY0, SX1, OY1)
random.seed(5)
pts1, pts2, pts3 = [], [], []; nz = 0
for i, x in enumerate(range(SX0, SX1 + 1, 4)):
    t = (x - SX0) / (SX1 - SX0)
    env = 0.55 + 0.45 * math.sin(t * math.pi * 3)
    pts1.append((x, int(mid + 70 * env * math.sin(t * math.pi * 22))))
    pts2.append((x, int(mid + 45 * math.sin(t * math.pi * 4 + 1.2))))
    nz = max(-60, min(60, nz + random.randint(-9, 9)))
    pts3.append((x, mid + nz))
poly(pts3, col=GREY, w=2, a=0.3)
poly(pts2, col=PEAK, w=2, a=0.5)
poly(pts1, a=0.9, w=2)
poly([(SX0, mid), (SX1, mid)], col=GREY, w=1, a=0.3)

# Spectrum analyser: filled curve with a few carriers, dashed peak-hold line above.
FY0, FY1 = 1790, 1990
scope_frame(SX0, FY0, SX1, FY1, vstep=54, hstep=50)
random.seed(7)
peaks = [(0.12, 0.9, 0.02), (0.31, 0.55, 0.03), (0.47, 0.75, 0.015), (0.66, 0.4, 0.04), (0.83, 0.65, 0.02)]
spec, hold = [], []
for x in range(SX0, SX1 + 1, 3):
    t = (x - SX0) / (SX1 - SX0)
    v = 0.08 + 0.06 * (1 - t) + sum(h * math.exp(-((t - c) ** 2) / (2 * w * w)) for c, h, w in peaks)
    v = max(0.02, min(0.95, v + random.uniform(-0.04, 0.04)))
    spec.append((x, int(FY1 - 4 - v * (FY1 - FY0 - 12))))
    hold.append((x, int(FY1 - 4 - min(0.97, v + 0.08 + 0.05 * math.sin(t * 40)) * (FY1 - FY0 - 12))))
area([(SX0, FY1 - 4)] + spec + [(SX1, FY1 - 4)], RED, 0.22)
poly(spec, a=0.9, w=2)
out.append(f"stroke '{LIGHT}' stroke-width 1 stroke-opacity 0.45 stroke-dasharray 6 8 fill-opacity 0 polyline {' '.join(f'{x},{y}' for x, y in hold)}")
out.append("stroke-dasharray none")

# Bottom row: radar sweep (left) and a Lissajous figure (right).
RY = 2105; RX = PX0 + 120; RR = 85
for r in (RR // 3, 2 * RR // 3, RR):
    out.append(f"stroke '{GREY}' stroke-width 2 stroke-opacity 0.45 fill-opacity 0 circle {RX},{RY} {RX + r},{RY}")
poly([(RX - RR, RY), (RX + RR, RY)], col=GREY, w=1, a=0.35); poly([(RX, RY - RR), (RX, RY + RR)], col=GREY, w=1, a=0.35)
a0, a1 = math.radians(-70), math.radians(-10)
sx, sy = RX + int(RR * math.cos(a0)), RY + int(RR * math.sin(a0)); ex, ey = RX + int(RR * math.cos(a1)), RY + int(RR * math.sin(a1))
out.append(f"stroke none fill '{RED}' fill-opacity 0.28 path 'M {RX},{RY} L {sx},{sy} A {RR},{RR} 0 0,1 {ex},{ey} Z'")
poly([(RX, RY), (ex, ey)], a=0.95, w=2)
random.seed(11)
for _ in range(4):
    ang = random.uniform(-math.pi, math.pi); rr = random.uniform(0.3, 0.9) * RR
    bxp, byp = RX + int(rr * math.cos(ang)), RY + int(rr * math.sin(ang))
    out.append(f"stroke none fill '{RED}' fill-opacity 0.9 circle {bxp},{byp} {bxp + 4},{byp}")
    out.append(f"stroke '{RED}' stroke-width 1 stroke-opacity 0.5 fill-opacity 0 circle {bxp},{byp} {bxp + 10},{byp}")
LX, LY = PX1 - 170, RY
liss = [(int(LX + 125 * math.sin(3 * t + math.pi / 2)), int(LY + 75 * math.sin(2 * t))) for t in [i * 2 * math.pi / 240 for i in range(241)]]
poly(liss, a=0.8, w=2, close=True)
poly([(LX - 135, LY), (LX + 135, LY)], col=GREY, w=1, a=0.3); poly([(LX, LY - 85), (LX, LY + 85)], col=GREY, w=1, a=0.3)

out.append("pop graphic-context")
print("\n".join(out))
