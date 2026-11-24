"""Composes the 1024x1024 front page from the tables in make_poster.py.

Build-time only: it uses Pillow and the device's system fonts, so it runs here and
the finished poster.png is what the entry ships. Run: python3 render.py

The layout is 3 leads + 8 cards + 12 briefs, sized so every headline is legible at
about 300 px across. Art is drawn into its own tile and pasted, so nothing can spill
outside a card.
"""

from PIL import Image, ImageDraw, ImageFont

from make_poster import (
    W, H, M, CW, PAPER, INK, GREY, NAVY, RED, AMBER, GREEN, HAIR,
    SERIF_B, SERIF_R, SANS_B, SANS_R,
    REGION, REGION_ORDER, REGION_LABEL, EDITION, VOLUME, DECK,
    LEADS, CARDS, BRIEFS, STATS, EXCLUDED, SHORT_PLACE,
)
from poster_art import ART

STATUS_COLOR = {
    "REPORTED": GREEN,
    "CLAIM": AMBER,
    "ONGOING": (31, 95, 168),
    "NOT ADOPTED": RED,
}

CARD_NUMBERS = (5, 6, 7, 8, 9, 10, 11, 13)
BRIEF_NUMBERS = tuple(b[0] for b in BRIEFS)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(s, f):
    return d.textlength(s, font=f)


def th(f):
    a, desc = f.getmetrics()
    return a + desc


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, path, maxw, maxh, hi, lo=7, leading=1.15):
    for s in range(int(hi), int(lo) - 1, -1):
        f = font(path, s)
        lines = wrap(text, f, maxw)
        if len(lines) * th(f) * leading <= maxh:
            return f, lines
    f = font(path, int(lo))
    return f, wrap(text, f, maxw)


def para(x, y, text, path, maxw, maxh, hi, color=INK, lo=7, leading=1.15,
         limit=None):
    """Draw wrapped text, never below `limit`. If the block at the minimum size
    would still overrun, the last line is dropped rather than spilling out."""
    f, lines = fit(text, path, maxw, maxh, hi, lo, leading)
    step = th(f) * leading
    if limit is not None:
        room = int((limit - y) // step)
        if room < 1:
            return y
        if len(lines) > room:
            lines = lines[:room]
            lines[-1] = lines[-1].rstrip(" ,.;:") + "\u2026"
    for i, ln in enumerate(lines):
        d.text((x, y + i * step), ln, font=f, fill=color)
    return y + len(lines) * step


def caps(x, y, s, size, color=INK, path=SANS_B, track=1.0, anchor="la"):
    f = font(path, int(round(size)))
    if abs(track - 1.0) < 0.01:
        d.text((x, y), s, font=f, fill=color, anchor=anchor)
        return tw(s, f)
    gap = size * (track - 1.0)
    width = sum(tw(ch, f) + gap for ch in s) - gap
    if anchor == "ma":
        x -= width / 2
    elif anchor == "ra":
        x -= width
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=color)
        cx += tw(ch, f) + gap
    return width


def hline(x0, y, x1, color=HAIR, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def art_block(kind, x, y, w, h, ground=(255, 255, 255)):
    """Draw one illustration in its own tile, then paste it: clips at the edges."""
    w, h = max(1, int(round(w))), max(1, int(round(h)))
    tile = Image.new("RGB", (w, h), ground)
    td = ImageDraw.Draw(tile)
    ART[kind](td, 0, 0, w, h)
    img.paste(tile, (int(round(x)), int(round(y))))


def status_chip(x, y, status, size):
    label = status
    f = font(SANS_B, int(round(size)))
    w = tw(label, f) + 6
    h = size + 4
    d.rectangle([x, y, x + w, y + h], fill=STATUS_COLOR.get(status, GREY))
    d.text((x + 3, y + 1.5), label, font=f, fill=(255, 255, 255))
    return w, h


def place_tab(x, y, place, color, size, maxw):
    """Draw the place tab. Uses a short label already chosen to fit, and shrinks
    the type rather than truncating mid-word if it still does not fit."""
    f = font(SANS_B, int(round(size)))
    label = place
    while tw(label, f) + 7 > maxw and f.size > 5:
        f = font(SANS_B, f.size - 1)
    w = tw(label, f) + 7
    h = size + 4
    d.rectangle([x, y, x + w, y + h], fill=color)
    d.text((x + 3.5, y + 1.5), label, font=f, fill=(255, 255, 255))
    return w, h


# ------------------------------------------------------------------- 1. nameplate ---
cards = [c for c in CARDS if c["n"] in CARD_NUMBERS]
briefs = [b for b in BRIEFS if b[0] in BRIEF_NUMBERS]
all_stories = LEADS + cards
TOTAL_STORIES = len(all_stories) + len(briefs)

STRIP_H = 22
d.rectangle([0, 0, W, STRIP_H], fill=NAVY)
caps(M, 7, "THE WORLD IN ONE DAY", 10, (255, 255, 255), track=1.12)
caps(W - M, 7, f"{TOTAL_STORIES} STORIES \u00b7 7 REGIONS \u00b7 ONE DAY", 10,
     (232, 200, 160), track=1.12, anchor="ra")

# --------------------------------------------------------------- 2. masthead ---
y = STRIP_H + 5
mf = font(SERIF_B, 68)
while tw(EDITION, mf) > CW - 4 and mf.size > 30:
    mf = font(SERIF_B, mf.size - 1)
d.text((M, y), EDITION, font=mf, fill=INK)
y += th(mf) * 0.98

df = font(SERIF_B, 14)
dlines = wrap(DECK, df, CW - 108)
for i, ln in enumerate(dlines[:2]):
    d.text((M, y + i * 16), ln, font=df, fill=RED)
caps(W - M, y + 2, VOLUME, 8.5, GREY, track=1.08, anchor="ra")
y += len(dlines[:2]) * 16 + 3
hline(M, y, W - M, HAIR, 3)
y += 5

# ------------------------------------------------------------ 3. region chips ---
counts = {}
for s in all_stories:
    counts[s["region"]] = counts.get(s["region"], 0) + 1
for b in briefs:
    counts[b[3]] = counts.get(b[3], 0) + 1

pill_h = 17
cx = M
for reg in REGION_ORDER:
    n = counts.get(reg, 0)
    if not n:
        continue
    label = f"{REGION_LABEL[reg]} {n}"
    f = font(SANS_B, 9)
    pw = tw(label, f) + 11
    d.rectangle([cx, y, cx + pw, y + pill_h], fill=REGION[reg])
    d.text((cx + 5.5, y + 3.5), label, font=f, fill=(255, 255, 255))
    cx += pw + 5
y += pill_h + 5

# ---------------------------------------------------------------- 4. UTC rail ---
RAIL_H = 22
d.rectangle([M, y, W - M, y + RAIL_H], fill=NAVY)
d.rectangle([M, y, M + 40, y + RAIL_H], fill=(255, 255, 255))
caps(M + 6, y + 6, "UTC", 9.5, NAVY, track=1.08)
rail = [
    ("00:00", "COP31 overtime opens in Antalya"),
    ("04:30", "Mines set three tankers ablaze in Hormuz"),
    ("09:00", "Nvidia board reinstates Huang"),
    ("14:20", "Nasdaq closes up 7%"),
]
rx = M + 46
for t, label in rail:
    tf = font(SANS_B, 8.6)
    d.text((rx, y + 6), t, font=tf, fill=AMBER)
    rx += tw(t, tf) + 4
    lf = font(SANS_B, 8.6)
    d.text((rx, y + 6), label, font=lf, fill=(255, 255, 255))
    rx += tw(label, lf) + 13
y += RAIL_H + 7

# ------------------------------------------------------ 5. leads + numbers rail ---
GUT = 8
BOX_W = 178
lead_w = (CW - BOX_W - GUT * 3) / 3
LEAD_H = 244
LEAD_ART = 84
lead_top = y

for i, s in enumerate(LEADS):
    x = M + i * (lead_w + GUT)
    col = REGION[s["region"]]
    d.rectangle([x, lead_top, x + lead_w, lead_top + LEAD_H], fill=(255, 255, 255),
                outline=(206, 200, 190))
    place_tab(x + 5, lead_top + 5, SHORT_PLACE.get(s["place"], s["place"]), col, 9,
              lead_w - 10)
    ay = lead_top + 5 + 14
    art_block(s["art"], x + 5, ay, lead_w - 10, LEAD_ART)
    status_chip(x + 9, ay + LEAD_ART - 15, s["status"], 8)
    ty = ay + LEAD_ART + 5
    caps(x + 6, ty, s["kicker"], 8.4, col, track=1.1)
    ty += 11
    ty = para(x + 6, ty, s["head"], SERIF_B, lead_w - 12, 66, 20, INK, leading=1.08,
              limit=lead_top + LEAD_H - 16)
    ty += 2
    ty = para(x + 6, ty, s["body"], SERIF_R, lead_w - 12, 74, 11.2, (48, 44, 40),
              leading=1.18, limit=lead_top + LEAD_H - 16)
    caps(x + 6, lead_top + LEAD_H - 14, s["src"], 7.2, GREY, track=1.02)

bx = W - M - BOX_W
d.rectangle([bx, lead_top, W - M, lead_top + LEAD_H], fill=NAVY)
caps(bx + 9, lead_top + 8, "THE DAY IN NUMBERS", 9.6, (255, 255, 255), track=1.1)
hline(bx + 9, lead_top + 24, W - M - 9, (70, 86, 118), 1)

# The rail is measured before it is drawn: every block's height is computed from the
# real font metrics, then the leftover space is split into even gaps. Nothing can
# run past the panel, which is what happened when the blocks were spaced by eye.
NUM_COL = 58
txt_x = bx + 9 + NUM_COL
txt_w = W - M - 9 - txt_x

blocks = []
for big, label, note in STATS:
    bf = font(SERIF_B, 30)
    while tw(big, bf) > NUM_COL - 8 and bf.size > 14:
        bf = font(SERIF_B, bf.size - 1)
    lf = font(SANS_B, 8.6)
    llines = wrap(label, lf, txt_w)
    nf = font(SANS_R, 8)
    nlines = wrap(note, nf, txt_w)
    h_txt = len(llines) * 10 + len(nlines) * 9.4
    h = max(th(bf), h_txt)
    blocks.append((big, bf, llines, lf, nlines, nf, h))

RAIL_TOP = lead_top + 30
RAIL_BOT = lead_top + LEAD_H - 8
room = RAIL_BOT - RAIL_TOP
used = sum(b[6] for b in blocks)
gap = (room - used) / max(1, len(blocks))
if gap < 2:
    raise SystemExit(f"numbers rail overflows by {-gap:.1f}px per block: "
                     f"need {used}, have {room}")

sy = RAIL_TOP
for big, bf, llines, lf, nlines, nf, h in blocks:
    d.text((bx + 9, sy - 3), big, font=bf, fill=(240, 170, 90))
    ytxt = sy + (h - (len(llines) * 10 + len(nlines) * 9.4)) / 2
    for ln in llines:
        d.text((txt_x, ytxt), ln, font=lf, fill=(255, 255, 255))
        ytxt += 10
    for ln in nlines:
        d.text((txt_x, ytxt), ln, font=nf, fill=(176, 190, 210))
        ytxt += 9.4
    sy += h + gap

# ------------------------------------------------------ 6. two rows of four cards ---
ROW_GUT = 8
card_w = (CW - ROW_GUT * 3) / 4
ROW_H = 178
CARD_ART = 66
row_tops = [lead_top + LEAD_H + 9, lead_top + LEAD_H + 9 + ROW_H + 8]

for idx, s in enumerate(cards):
    row, col_i = divmod(idx, 4)
    x = M + col_i * (card_w + ROW_GUT)
    top = row_tops[row]
    col = REGION[s["region"]]
    d.rectangle([x, top, x + card_w, top + ROW_H], fill=(255, 255, 255),
                outline=(206, 200, 190))
    place_tab(x + 5, top + 5, SHORT_PLACE.get(s["place"], s["place"]), col, 8,
              card_w - 10)
    ay = top + 5 + 13
    art_block(s["art"], x + 5, ay, card_w - 10, CARD_ART)
    status_chip(x + 8, ay + CARD_ART - 14, s["status"], 7.4)
    ty = ay + CARD_ART + 5
    caps(x + 5, ty, s["kicker"], 7.6, col, track=1.08)
    ty += 10
    ty = para(x + 5, ty, s["head"], SERIF_B, card_w - 10, 46, 14.6, INK, leading=1.06,
              limit=top + ROW_H - 4)
    ty += 2
    ty = para(x + 5, ty, s["body"], SERIF_R, card_w - 10, 32, 9.2, (54, 50, 46),
              leading=1.16, limit=top + ROW_H - 4)

# ------------------------------------------------------------ 7. briefs + map ---
by = row_tops[1] + ROW_H + 8
BRIEF_H = 104
MAP_W = 252
brief_w = CW - MAP_W - 8
d.rectangle([M, by, M + brief_w, by + 16], fill=NAVY)
caps(M + 6, by + 4, "ALSO ON TUESDAY 24 NOVEMBER", 9.2, (255, 255, 255), track=1.1)
lx = M + brief_w - 7
for label, colr in [("ONGOING", STATUS_COLOR["ONGOING"]), ("CLAIM", AMBER),
                    ("REPORTED", GREEN)]:
    f = font(SANS_B, 7)
    lw = tw(label, f) + 7
    lx -= lw
    d.rectangle([lx, by + 4.5, lx + lw, by + 13], fill=colr)
    d.text((lx + 3.5, by + 6), label, font=f, fill=(255, 255, 255))
    lx -= 5

col_w = (brief_w - 14) / 2
rows_per_col = 6
for i, (num, place, head, region, lat, lon) in enumerate(briefs):
    c, r = divmod(i, rows_per_col)
    xx = M + 4 + c * (col_w + 8)
    yy = by + 21 + r * 14.6
    nf = font(SANS_B, 8.6)
    # Continue the numbering from the 11 stories above, so the run reads 12..23 and
    # matches the total in the nameplate.
    d.text((xx, yy), f"{12 + i}", font=nf, fill=REGION[region])
    pf = font(SANS_B, 7.2)
    d.text((xx + 15, yy + 1), place, font=pf, fill=GREY)
    hf = font(SERIF_B, 8.4)
    lead_in = xx + 15 + tw(place, pf) + 5
    avail = xx + col_w - lead_in
    txt = head
    if tw(txt, hf) > avail:
        while len(txt) > 8 and tw(txt + "\u2026", hf) > avail:
            txt = txt[:-1]
        txt = txt.rstrip(" ,;:") + "\u2026"
    d.text((lead_in, yy), txt, font=hf, fill=INK)

# map panel
mx = W - M - MAP_W
d.rectangle([mx, by, W - M, by + BRIEF_H], fill=(255, 255, 255), outline=(206, 200, 190))
caps(mx + 7, by + 5, "WHERE IT HAPPENED", 8.6, NAVY, track=1.1)
caps(W - M - 7, by + 6, "PIN COLOUR = REGION", 6.4, GREY, track=1.0, anchor="ra")

CONTINENTS = [
    # North America, with Central America reaching down to meet South America so the
    # two do not read as separate islands.
    [(-168, 65), (-140, 70), (-120, 72), (-95, 72), (-80, 68), (-60, 60), (-55, 48),
     (-66, 44), (-70, 42), (-75, 36), (-81, 30), (-83, 26), (-88, 21), (-92, 16),
     (-84, 10), (-79, 9), (-78, 7), (-83, 8), (-88, 13), (-95, 16), (-105, 22),
     (-115, 30), (-125, 40), (-130, 55), (-150, 60)],
    [(-79, 9), (-72, 11), (-62, 11), (-50, 4), (-35, -5), (-38, -15), (-48, -25),
     (-58, -38), (-65, -52), (-72, -52), (-75, -40), (-70, -20), (-80, -5), (-78, 2)],
    [(-10, 36), (0, 44), (10, 45), (20, 40), (28, 36), (33, 31), (35, 32), (36, 37),
     (30, 42), (30, 45), (28, 55), (20, 60), (10, 58), (4, 52), (-5, 48), (-10, 42)],
    [(-17, 15), (0, 15), (15, 15), (32, 30), (35, 15), (42, 10), (50, 2), (42, -12),
     (35, -22), (25, -34), (18, -34), (12, -18), (8, -5), (0, 5), (-10, 5)],
    [(30, 45), (45, 42), (55, 40), (60, 25), (70, 20), (78, 8), (88, 22), (98, 10),
     (105, 1), (110, 10), (120, 22), (122, 32), (128, 38), (135, 45), (145, 48),
     (155, 58), (170, 65), (180, 68), (180, 71), (160, 72), (140, 72), (120, 74),
     (100, 76), (80, 74), (60, 70), (50, 60), (40, 55)],
    [(114, -22), (122, -18), (130, -12), (142, -11), (150, -22), (153, -28),
     (148, -38), (140, -38), (130, -32), (118, -34), (114, -28)],
    [(-8, 51), (-5, 58), (-2, 58), (0, 51)],
    [(130, 31), (136, 35), (141, 41), (145, 44), (142, 38), (137, 34)],
    [(166, -46), (174, -41), (176, -38), (170, -44)],
    # Madagascar, Japan, and the Indonesian arc: without them the pins for Antananarivo,
    # Seoul and Jakarta would sit in bare ocean.
    [(43, -12), (50, -15), (50, -25), (45, -25), (43, -18)],
    [(130, 31), (141, 41), (146, 44), (143, 42), (138, 35), (132, 32)],
    [(95, 5), (105, 0), (115, -3), (125, -6), (135, -3), (140, -6), (130, 0),
     (120, 2), (110, 3), (100, 6)],
    [(-60, -52), (-58, -54), (-66, -55), (-70, -53), (-68, -50)],
]


def in_poly(px, py, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py):
            xint = (xj - xi) * (py - yi) / (yj - yi) + xi
            if px < xint:
                inside = not inside
        j = i
    return inside


MAP_TOP = by + 18
MAP_BOT = by + BRIEF_H - 4
MAP_LEFT = mx + 6
MAP_RIGHT = W - M - 6

# The projection covers -46..78 degrees only: the pins all sit in that band, so the
# empty polar rows that used to eat a third of the panel are dropped.
LAT_TOP, LAT_BOT = 78.0, -46.0

d.rectangle([MAP_LEFT - 2, MAP_TOP, MAP_RIGHT + 2, MAP_BOT], fill=(238, 243, 246))


def proj(lat, lon):
    px = MAP_LEFT + (lon + 180) / 360 * (MAP_RIGHT - MAP_LEFT)
    py = MAP_TOP + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * (MAP_BOT - MAP_TOP)
    return px, py


lat = LAT_TOP
while lat >= LAT_BOT:
    lon = -178.0
    while lon <= 178:
        if any(in_poly(lon, lat, poly) for poly in CONTINENTS):
            d.point(proj(lat, lon), fill=(120, 136, 150))
            px, py = proj(lat, lon)
            d.point((px + 0.9, py), fill=(140, 154, 166))
        lon += 2.2
    lat -= 2.6

pins = [(s["n"], s["lat"], s["lon"], s["region"]) for s in all_stories]
pins += [(b[0], b[4], b[5], b[3]) for b in briefs]
for num, lat_, lon_, region in pins:
    px, py = proj(lat_, lon_)
    # A soft disc under each pin so an island location reads as a place, not a speck
    # floating in open water.
    d.ellipse([px - 4.4, py - 4.4, px + 4.4, py + 4.4], fill=(226, 232, 236))
    d.ellipse([px - 2.9, py - 2.9, px + 2.9, py + 2.9], fill=REGION[region])
    d.ellipse([px - 0.9, py - 0.9, px + 0.9, py + 0.9], fill=(255, 255, 255))

# ------------------------------------------------------------------ 8. footer ---
fy = by + BRIEF_H + 6
FOOT_H = H - M - fy
if FOOT_H < 60:
    raise SystemExit(f"footer needs at least 60px, only {FOOT_H:.0f} left")

d.rectangle([M, fy, W - M, fy + FOOT_H], fill=(255, 255, 255), outline=RED, width=2)

foot_text = ("Every story on this page happened, or was first reported, on Tuesday "
             "24 November 2026 (UTC). The deadline falls after that day has ended "
             "everywhere on Earth.")
LEFT_W = 486
ff = font(SERIF_R, 10)
flines = wrap(foot_text, ff, LEFT_W)
fstep = th(ff) * 1.2

ex_x = M + 512
EX_W = W - M - 8 - ex_x
ef = font(SERIF_R, 8)
ex_lines = []
cur = ""
for item in EXCLUDED:
    trial = (cur + " \u00b7 " + item) if cur else item
    if tw(trial, ef) <= EX_W:
        cur = trial
    else:
        if cur:
            ex_lines.append(cur)
        cur = item
if cur:
    ex_lines.append(cur)

HEAD_H = 15
body_needed = max(len(flines) * fstep, len(ex_lines) * 11)
HOW_H = 16
needed = HEAD_H + body_needed + HOW_H + 10
if needed > FOOT_H:
    raise SystemExit(f"footer content needs {needed:.0f}px, box is {FOOT_H:.0f}px")

caps(M + 8, fy + 5, "DATE CHECK", 9.4, RED, track=1.12)
for i, ln in enumerate(flines):
    d.text((M + 8, fy + HEAD_H + i * fstep), ln, font=ff, fill=(46, 42, 38))

caps(ex_x, fy + 5, "LEFT OUT \u2014 REPORTED ON AN EARLIER DAY", 7.4, RED, track=1.05)
for i, ln in enumerate(ex_lines[:4]):
    yy = fy + HEAD_H + i * 11
    d.text((ex_x, yy), ln, font=ef, fill=(146, 138, 130))
    d.line([(ex_x, yy + 4.4), (ex_x + tw(ln, ef), yy + 4.4)], fill=(146, 138, 130),
           width=1)

how_y = fy + FOOT_H - 15
caps(M + 8, how_y,
     "HOW SURE  \u00b7  REPORTED = CARRIED BY THE DAY'S WIRES OR OFFICIALS  \u00b7  "
     "CLAIM = ONE SIDE'S ACCOUNT, LABELLED AS SUCH  \u00b7  ONGOING = STILL UNFOLDING",
     6.6, GREY, track=1.0)
caps(M + 8, how_y + 8,
     "SCENES ARE DRAWN ILLUSTRATIONS, NOT PHOTOGRAPHS  \u00b7  ALL TIMES UTC",
     6.0, (150, 142, 134), track=1.0)

img.save("poster.png", optimize=True)
print("poster.png", img.size)
print(f"lead_top={lead_top} rows={row_tops} briefs_top={by} footer={fy:.0f} "
      f"foot_h={FOOT_H:.0f} ends={fy + FOOT_H:.0f}")
