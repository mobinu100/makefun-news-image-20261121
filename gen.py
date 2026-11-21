#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261121.

A typographic newspaper front page, 1024x1024, drawn with PIL only.
Deterministic: no timestamps, no randomness, no network, fixed fonts.
Run: python3 gen.py  (writes entry.png next to this file)
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
PAPER = (253, 251, 244)
INK = (12, 12, 12)
RED = (166, 25, 25)
GREY = (90, 90, 90)
RULE = (40, 40, 40)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_COND_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-CondensedBold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# (headline, deck) -- exactly the 18 stories, verbatim, in order.
STORIES = [
    ("ICJ: Myanmar committed genocide against Rohingya",
     "Court orders reparations for Rohingya"),
    ("AP: Russian missiles land in Poland",
     "Tusk calls it intentional provocation"),
    ("Reuters: Russia hits Kyiv bridges, 9 dead",
     "Drones hit Kyiv overnight"),
    ("Reuters: Kryvyi Rih strike kills 2, injures 42",
     "Boy and paramedic among dead"),
    ("EU: \u20ac1bn military aid for Ukraine",
     "\u20ac7.9bn also disbursed to Kyiv"),
    ("WSJ: US floated NATO for Ukraine",
     "Zelensky: no territory conceded"),
    ("Reuters: Denmark says Russia plotted rapper killing",
     "Two charged, attach\u00e9 expelled"),
    ("Reuters: Saudi intercepts 3 missiles over Riyadh",
     "Day after PIF tower hit"),
    ("Reuters: Trump threatens tax on overseas data centres",
     "US firms face penalties abroad"),
    ("Reuters: US approved 879,000 AI chips for China",
     "House panel cites six-month approvals"),
    ("WSJ: Nasdaq falls 5.2% as Anthropic slides",
     "Anthropic closes at $89"),
    ("Reuters: Senate rejects Iran war powers vote",
     "Vote fails 51 to 48"),
    ("US: Sanctions hit Comancheros and \u2019Ndrangheta",
     "Drug groups linked to cartels"),
    ("Reuters: Mongolia president resigns, election due",
     "Parliament approves resignation Thursday"),
    ("Argentina: Senate backs disability law 71-0",
     "Pensions set at 70% minimum"),
    ("Reuters: Gupta gets 19 years in US plot",
     "Target was Sikh activist Pannun"),
    ("UK: 1,000 drones for Ukraine in \u00a3260m package",
     "Long-range strike drones from Berlin"),
    ("Reuters: EU-UK agree youth scheme",
     "100,000 places a year"),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, max_w, max_lines=2):
    """Largest headline size (31 down to 26) that wraps into max_lines."""
    for size in range(31, 25, -1):
        fnt = font(SERIF_COND_BOLD, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size
    fnt = font(SERIF_COND_BOLD, 26)
    return fnt, wrap(draw, text, fnt, max_w), 26


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ---
    title_f = font(SERIF_BOLD, 86)
    title = "THE WORLD"
    tw = d.textlength(title, font=title_f)
    d.text(((W - tw) / 2, 10), title, font=title_f, fill=INK)
    d.rectangle([28, 104, W - 28, 107], fill=RED)
    date_f = font(SANS_BOLD, 32)
    date = "SATURDAY 21 NOVEMBER 2026"
    dw = d.textlength(date, font=date_f)
    d.text(((W - dw) / 2, 116), date, font=date_f, fill=RED)
    d.rectangle([28, 156, W - 28, 160], fill=INK)

    # --- story grid: 3 columns x 6 rows ---
    margin = 28
    gutter = 18
    col_w = (W - 2 * margin - 2 * gutter) // 3
    grid_top = 164
    grid_bottom = 1016
    row_h = (grid_bottom - grid_top) // 6
    kicker_f = font(SANS_BOLD, 20)
    deck_f = font(SANS, 26)

    for idx, (headline, deck) in enumerate(STORIES):
        col = idx % 3
        row = idx // 3
        x0 = margin + col * (col_w + gutter)
        y0 = grid_top + row * row_h
        pad = 8
        tx = x0 + pad
        text_w = col_w - 2 * pad
        y = y0 + 2

        # kicker
        d.text((tx, y), "21 NOV", font=kicker_f, fill=RED)
        y += 23
        # headline, fitted to two lines
        hf, hlines, _hsize = fit_headline(d, headline, text_w)
        for line in hlines[:2]:
            d.text((tx, y), line, font=hf, fill=INK)
            y += 30
        # deck, 26px, at most two lines
        dlines = wrap(d, deck, deck_f, text_w)
        for line in dlines[:2]:
            d.text((tx, y), line, font=deck_f, fill=(40, 40, 40))
            y += 26

        # vertical divider (not after last column)
        if col < 2:
            vx = x0 + col_w + gutter // 2
            d.line([(vx, y0 + 6), (vx, y0 + row_h - 6)], fill=RULE, width=1)
        # horizontal divider (not after last row)
        if row < 5:
            hy = y0 + row_h
            d.line([(x0, hy), (x0 + col_w, hy)], fill=RULE, width=1)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
