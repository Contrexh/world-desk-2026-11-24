# ---- drawing helpers and flat-vector art, used by render.py ----

from PIL import ImageFont

from make_poster import (RED, AMBER, NAVY, INK, GREY, HAIR, PAPER, GREEN,
                         SANS_B, SANS_R, SERIF_B, SERIF_R,
                         CARDS_SELECTED, BRIEFS_SELECTED)


def font(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, f):
    return d.textlength(s, font=f)


def th(f):
    a, desc = f.getmetrics()
    return a + desc


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, path, maxw, maxh, hi, lo=6):
    """Largest size whose wrapped text fits the box."""
    for s in range(hi, lo - 1, -1):
        f = font(path, s)
        lines = wrap(d, text, f, maxw)
        if len(lines) * th(f) * 1.16 <= maxh:
            return f, lines
    f = font(path, lo)
    return f, wrap(d, text, f, maxw)


def para(d, x, y, text, path, maxw, maxh, hi, color=INK, lo=6, leading=1.16):
    f, lines = fit(d, text, path, maxw, maxh, hi, lo)
    step = th(f) * leading
    for i, ln in enumerate(lines):
        d.text((x, y + i * step), ln, font=f, fill=color)
    return y + len(lines) * step


def caps(d, x, y, s, size, color=INK, path=SANS_B, track=1.0, anchor="la"):
    """Letter-spaced capitals; track 1.0 means natural spacing."""
    f = font(path, size)
    if track == 1.0:
        d.text((x, y), s, font=f, fill=color, anchor=anchor)
        return tw(d, s, f)
    gap = size * (track - 1.0)
    w = sum(tw(d, ch, f) + gap for ch in s) - gap
    if anchor == "ma":
        x -= w / 2
    elif anchor == "ra":
        x -= w
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=color)
        cx += tw(d, ch, f) + gap
    return w


def hline(d, x0, y, x1, color=HAIR, w=1):
    d.line([(x0, y), (x1, y)], fill=color, width=w)


def vline(d, x, y0, y1, color=HAIR, w=1):
    d.line([(x, y0), (x, y1)], fill=color, width=w)


# ------------------------------------------------------------------- the art ---

def _frame(d, x, y, w, h, fill):
    d.rectangle([x, y, x + w, y + h], fill=fill)


def art_tanker(d, x, y, w, h):
    _frame(d, x, y, w, h, (36, 62, 92))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(24, 44, 70))
    for i in range(3):
        cx = x + w * (0.22 + i * 0.28)
        d.ellipse([cx - w * 0.11, y + h * 0.30, cx + w * 0.11, y + h * 0.56],
                  fill=(90, 96, 104))
        d.rectangle([cx - w * 0.09, y + h * 0.50, cx + w * 0.09, y + h * 0.60],
                    fill=(70, 76, 84))
        if i != 1:
            d.polygon([(cx - w * 0.07, y + h * 0.30), (cx + w * 0.07, y + h * 0.30),
                       (cx + w * 0.02, y + h * 0.10), (cx - w * 0.03, y + h * 0.10)],
                      fill=RED)
    for i in range(8):
        d.arc([x + w * 0.05 + i * w * 0.11, y + h * 0.66,
               x + w * 0.19 + i * w * 0.11, y + h * 0.76], 200, 340,
              fill=(150, 168, 186))


def art_talks(d, x, y, w, h):
    _frame(d, x, y, w, h, (226, 232, 236))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(196, 204, 210))
    d.ellipse([x + w * 0.30, y + h * 0.26, x + w * 0.70, y + h * 0.66],
              fill=(250, 250, 248), outline=(120, 126, 130), width=2)
    d.line([(x + w * 0.50, y + h * 0.30), (x + w * 0.50, y + h * 0.44)],
           fill=INK, width=2)
    d.line([(x + w * 0.50, y + h * 0.44), (x + w * 0.60, y + h * 0.50)],
           fill=INK, width=2)
    for i, col in enumerate([(31, 95, 168), (194, 27, 44), (201, 138, 43)]):
        d.rectangle([x + w * (0.06 + i * 0.07), y + h * 0.10,
                     x + w * (0.11 + i * 0.07), y + h * 0.56], fill=col)
    d.rectangle([x + w * 0.30, y + h * 0.74, x + w * 0.70, y + h * 0.86],
                fill=(120, 126, 130))


def art_chart(d, x, y, w, h):
    _frame(d, x, y, w, h, (18, 26, 40))
    pts = [(0.04, 0.86), (0.18, 0.78), (0.30, 0.84), (0.44, 0.54),
           (0.58, 0.62), (0.70, 0.30), (0.84, 0.36), (0.96, 0.10)]
    poly = [(x + w * a, y + h * b) for a, b in pts]
    d.polygon(poly + [(x + w * 0.96, y + h), (x + w * 0.04, y + h)],
              fill=(26, 52, 78))
    d.line(poly, fill=(64, 200, 140), width=3, joint="curve")
    for i in range(4):
        yy = y + h * (0.86 - i * 0.22)
        d.line([(x + w * 0.04, yy), (x + w * 0.96, yy)], fill=(38, 48, 62))


def art_drone(d, x, y, w, h):
    _frame(d, x, y, w, h, (22, 30, 48))
    for i in range(9):
        d.ellipse([x + w * 0.05 + i * w * 0.10, y + h * 0.12 + (i % 3) * h * 0.03,
                   x + w * 0.07 + i * w * 0.10, y + h * 0.14 + (i % 3) * h * 0.03],
                  fill=(200, 210, 220))
    d.polygon([(x + w * 0.18, y + h * 0.92), (x + w * 0.82, y + h * 0.92),
               (x + w * 0.72, y + h * 0.52), (x + w * 0.28, y + h * 0.52)],
              fill=(46, 54, 66))
    for i in range(4):
        d.rectangle([x + w * (0.26 + i * 0.13), y + h * 0.60,
                     x + w * (0.32 + i * 0.13), y + h * 0.68], fill=AMBER)
    d.line([(x + w * 0.50, y + h * 0.30), (x + w * 0.50, y + h * 0.50)],
           fill=(230, 120, 70), width=2)
    d.ellipse([x + w * 0.44, y + h * 0.24, x + w * 0.56, y + h * 0.36],
              outline=(230, 120, 70), width=2)


def art_rubble(d, x, y, w, h):
    _frame(d, x, y, w, h, (58, 62, 70))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(40, 44, 50))
    d.rectangle([x + w * 0.10, y + h * 0.22, x + w * 0.78, y + h * 0.78],
                fill=(96, 98, 104))
    for r in range(3):
        for c in range(4):
            if (r + c) % 3 == 0:
                continue
            d.rectangle([x + w * (0.15 + c * 0.15), y + h * (0.28 + r * 0.15),
                         x + w * (0.25 + c * 0.15), y + h * (0.39 + r * 0.15)],
                        fill=(32, 34, 38))
    d.polygon([(x + w * 0.70, y + h * 0.22), (x + w * 0.92, y + h * 0.34),
               (x + w * 0.88, y + h * 0.78), (x + w * 0.72, y + h * 0.60)],
              fill=(70, 72, 78))
    d.polygon([(x + w * 0.05, y + h * 0.86), (x + w * 0.30, y + h * 0.72),
               (x + w * 0.48, y + h * 0.90)], fill=(120, 118, 112))


def art_strike(d, x, y, w, h):
    _frame(d, x, y, w, h, (30, 34, 40))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(24, 26, 30))
    d.polygon([(x + w * 0.12, y + h * 0.72), (x + w * 0.34, y + h * 0.40),
               (x + w * 0.56, y + h * 0.72)], fill=(64, 66, 72))
    d.line([(x + w * 0.30, y + h * 0.72), (x + w * 0.30, y + h * 0.34)],
           fill=(150, 152, 158), width=2)
    for i, rad in enumerate([0.10, 0.18, 0.26]):
        d.ellipse([x + w * 0.30 - w * rad, y + h * 0.34 - w * rad,
                   x + w * 0.30 + w * rad, y + h * 0.34 + w * rad],
                  outline=(230, 140, 70))
    d.polygon([(x + w * 0.62, y + h * 0.12), (x + w * 0.72, y + h * 0.40),
               (x + w * 0.66, y + h * 0.40), (x + w * 0.74, y + h * 0.62),
               (x + w * 0.60, y + h * 0.34), (x + w * 0.66, y + h * 0.34)],
              fill=(240, 190, 90))


def art_factory(d, x, y, w, h):
    _frame(d, x, y, w, h, (44, 40, 38))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(30, 26, 24))
    d.rectangle([x + w * 0.08, y + h * 0.34, x + w * 0.56, y + h * 0.70],
                fill=(96, 88, 80))
    for i in range(3):
        d.rectangle([x + w * (0.12 + i * 0.15), y + h * 0.42,
                     x + w * (0.21 + i * 0.15), y + h * 0.54], fill=(240, 190, 90))
    d.rectangle([x + w * 0.62, y + h * 0.16, x + w * 0.74, y + h * 0.70],
                fill=(110, 100, 92))
    for i in range(4):
        cx = x + w * (0.68 + (i % 2) * 0.04)
        cy = y + h * (0.10 - i * 0.05)
        d.ellipse([cx - w * 0.09, cy - h * 0.06, cx + w * 0.09, cy + h * 0.06],
                  fill=(150, 138, 126))
    for i, hh in enumerate([0.44, 0.36, 0.48]):
        bx = x + w * (0.20 + i * 0.22)
        d.polygon([(bx, y + h * 0.78), (bx + w * 0.07, y + h * (0.78 - hh * 0.30)),
                   (bx + w * 0.14, y + h * 0.78)], fill=(250, 170, 60))


def art_crash(d, x, y, w, h):
    _frame(d, x, y, w, h, (150, 158, 164))
    d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(74, 78, 82))
    d.rectangle([x + w * 0.06, y + h * 0.34, x + w * 0.52, y + h * 0.66],
                fill=(236, 196, 60))
    for i in range(4):
        d.rectangle([x + w * (0.10 + i * 0.10), y + h * 0.38,
                     x + w * (0.17 + i * 0.10), y + h * 0.50], fill=(60, 66, 72))
    d.rectangle([x + w * 0.52, y + h * 0.30, x + w * 0.94, y + h * 0.64],
                fill=(190, 60, 60))
    d.polygon([(x + w * 0.52, y + h * 0.30), (x + w * 0.60, y + h * 0.10),
               (x + w * 0.78, y + h * 0.10), (x + w * 0.86, y + h * 0.30)],
              fill=(170, 50, 50))
    d.line([(x + w * 0.44, y + h * 0.78), (x + w * 0.62, y + h * 0.70)],
           fill=(250, 250, 250), width=2)
    d.ellipse([x + w * 0.14, y + h * 0.62, x + w * 0.24, y + h * 0.78], fill=(30, 30, 30))
    d.ellipse([x + w * 0.74, y + h * 0.62, x + w * 0.84, y + h * 0.78], fill=(30, 30, 30))


def art_megaphone(d, x, y, w, h):
    _frame(d, x, y, w, h, (206, 196, 180))
    d.polygon([(x + w * 0.22, y + h * 0.46), (x + w * 0.52, y + h * 0.20),
               (x + w * 0.52, y + h * 0.76), (x + w * 0.22, y + h * 0.54)],
              fill=(60, 60, 64))
    d.rectangle([x + w * 0.14, y + h * 0.44, x + w * 0.24, y + h * 0.56],
                fill=(40, 40, 44))
    for i, rad in enumerate([0.08, 0.15, 0.22]):
        d.arc([x + w * 0.52 - w * rad, y + h * 0.48 - h * rad,
               x + w * 0.52 + w * rad, y + h * 0.48 + h * rad], -55, 55,
              fill=RED, width=2)
    d.rectangle([x + w * 0.06, y + h * 0.80, x + w * 0.44, y + h * 0.88], fill=NAVY)
    for i in range(3):
        d.ellipse([x + w * (0.60 + i * 0.12), y + h * 0.80,
                   x + w * (0.64 + i * 0.12), y + h * 0.84], fill=(90, 80, 70))


def art_gavel(d, x, y, w, h):
    _frame(d, x, y, w, h, (232, 228, 220))
    d.rectangle([x + w * 0.20, y + h * 0.66, x + w * 0.80, y + h * 0.80],
                fill=(120, 96, 70))
    d.rectangle([x + w * 0.46, y + h * 0.80, x + w * 0.54, y + h * 0.92],
                fill=(100, 80, 58))
    d.rectangle([x + w * 0.24, y + h * 0.34, x + w * 0.62, y + h * 0.52],
                fill=(96, 74, 52))
    d.rectangle([x + w * 0.60, y + h * 0.42, x + w * 0.86, y + h * 0.48],
                fill=(120, 96, 70))
    for i in range(3):
        d.line([(x + w * (0.30 + i * 0.10), y + h * 0.16),
                (x + w * (0.34 + i * 0.10), y + h * 0.30)], fill=(150, 150, 150), width=2)


def art_concert(d, x, y, w, h):
    _frame(d, x, y, w, h, (18, 16, 26))
    for i in range(5):
        d.line([(x + w * (0.10 + i * 0.20), y), (x + w * (0.02 + i * 0.20), y + h * 0.50)],
               fill=(58, 44, 88), width=3)
    d.ellipse([x + w * 0.42, y + h * 0.06, x + w * 0.58, y + h * 0.22],
              fill=(240, 208, 90))
    for i in range(7):
        cx = x + w * (0.08 + i * 0.14)
        d.ellipse([cx - w * 0.05, y + h * 0.52, cx + w * 0.05, y + h * 0.72],
                  fill=(200, 170, 150))
        d.polygon([(cx - w * 0.07, y + h), (cx + w * 0.07, y + h),
                   (cx + w * 0.05, y + h * 0.68), (cx - w * 0.05, y + h * 0.68)],
                  fill=(70, 60, 80))
    for i in range(5):
        d.arc([x + w * 0.20, y + h * 0.30, x + w * (0.24 + i * 0.06), y + h * 0.44],
              0, 360, fill=(120, 90, 160))


def art_school(d, x, y, w, h):
    _frame(d, x, y, w, h, (198, 206, 214))
    d.rectangle([x, y + h * 0.70, x + w, y + h], fill=(84, 92, 100))
    d.rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.86, y + h * 0.72],
                fill=(224, 210, 186))
    d.polygon([(x + w * 0.10, y + h * 0.30), (x + w * 0.50, y + h * 0.06),
               (x + w * 0.90, y + h * 0.30)], fill=(150, 90, 80))
    for i in range(4):
        d.rectangle([x + w * (0.20 + i * 0.17), y + h * 0.38,
                     x + w * (0.30 + i * 0.17), y + h * 0.52], fill=(90, 110, 130))
    d.rectangle([x + w * 0.44, y + h * 0.56, x + w * 0.56, y + h * 0.72],
                fill=(110, 80, 60))
    d.ellipse([x + w * 0.70, y + h * 0.44, x + w * 0.88, y + h * 0.62], fill=RED)
    d.text((x + w * 0.79, y + h * 0.48), "!", font=font(SANS_B, max(8, int(w * 0.16))),
           fill=(255, 255, 255), anchor="ma")


def art_jet(d, x, y, w, h):
    _frame(d, x, y, w, h, (120, 150, 180))
    for i in range(4):
        d.line([(x, y + h * (0.2 + i * 0.18)), (x + w, y + h * (0.28 + i * 0.16))],
               fill=(146, 172, 196), width=1)
    d.polygon([(x + w * 0.30, y + h * 0.54), (x + w * 0.74, y + h * 0.42),
               (x + w * 0.74, y + h * 0.50), (x + w * 0.34, y + h * 0.60)],
              fill=(70, 76, 86))
    d.polygon([(x + w * 0.46, y + h * 0.52), (x + w * 0.34, y + h * 0.30),
               (x + w * 0.44, y + h * 0.32), (x + w * 0.54, y + h * 0.51)],
              fill=(90, 96, 106))
    d.polygon([(x + w * 0.62, y + h * 0.48), (x + w * 0.70, y + h * 0.68),
               (x + w * 0.62, y + h * 0.66), (x + w * 0.56, y + h * 0.49)],
              fill=(90, 96, 106))
    d.ellipse([x + w * 0.72, y + h * 0.44, x + w * 0.78, y + h * 0.50], fill=AMBER)


def art_sea(d, x, y, w, h):
    _frame(d, x, y, w, h, (24, 66, 96))
    for i in range(6):
        d.line([(x, y + h * (0.30 + i * 0.12)), (x + w, y + h * (0.32 + i * 0.12))],
               fill=(38, 92, 128), width=2)
    d.rectangle([x + w * 0.06, y + h * 0.44, x + w * 0.94, y + h * 0.70],
                fill=(20, 50, 76))
    d.rectangle([x + w * 0.40, y + h * 0.08, x + w * 0.60, y + h * 0.44],
                fill=(60, 120, 160))
    d.line([(x + w * 0.50, y + h * 0.08), (x + w * 0.50, y + h * 0.44)],
           fill=(200, 220, 235), width=2)
    for i in range(4):
        d.ellipse([x + w * (0.12 + i * 0.20), y + h * 0.78,
                   x + w * (0.20 + i * 0.20), y + h * 0.86], fill=(240, 200, 90))


ART = {
    "tanker": art_tanker, "talks": art_talks, "chart": art_chart,
    "drone": art_drone, "rubble": art_rubble, "strike": art_strike,
    "factory": art_factory, "crash": art_crash, "megaphone": art_megaphone,
    "gavel": art_gavel, "concert": art_concert, "school": art_school,
    "jet": art_jet, "sea": art_sea,
}
