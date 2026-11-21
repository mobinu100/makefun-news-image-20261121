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
    """Largest headline size (26 down to 22) that wraps into max_lines.

    22 is the floor: at text_w 304 every story fits in two lines at 22.
    Sizes below that would put headlines far under the 26px decks.
    """
    for size in range(26, 21, -1):
        fnt = font(SERIF_COND_BOLD, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines, size
    fnt = font(SERIF_COND_BOLD, 22)
    return fnt, wrap(draw, text, fnt, max_w), 22


def draw_ink(draw, x, ink_top, text, fnt, fill):
    """Draw text with its ink top at ink_top (not the em-box top).

    PIL places text by the em box, whose ascent+descent padding is what
    caused deck/headline collisions when lines were stepped by fixed
    amounts. Placing by measured ink bounds gives exact, gap-controlled
    spacing. Returns the ink height of the drawn text.
    """
    b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - b[0], ink_top - b[1]), text, font=fnt, fill=fill)
    return b[3] - b[1]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead (ink-placed, metric-driven) ---
    title_f = font(SERIF_BOLD, 76)
    title = "THE WORLD"
    tw = d.textlength(title, font=title_f)
    tb = d.textbbox((0, 0), title, font=title_f)
    d.text(((W - tw) / 2 - tb[0], 10 - tb[1]), title, font=title_f, fill=INK)
    title_bottom = 10 + (tb[3] - tb[1])
    d.rectangle([28, title_bottom + 8, W - 28, title_bottom + 11], fill=RED)
    date_f = font(SANS_BOLD, 28)
    date = "SATURDAY 21 NOVEMBER 2026"
    dw = d.textlength(date, font=date_f)
    db = d.textbbox((0, 0), date, font=date_f)
    date_top = title_bottom + 19
    d.text(((W - dw) / 2 - db[0], date_top - db[1]), date, font=date_f, fill=RED)
    date_bottom = date_top + (db[3] - db[1])
    d.rectangle([28, date_bottom + 8, W - 28, date_bottom + 11], fill=INK)

    # --- story grid: 3 columns x 6 rows ---
    margin = 24
    gutter = 14
    col_w = (W - 2 * margin - 2 * gutter) // 3
    grid_top = date_bottom + 17
    grid_bottom = 1020
    row_h = (grid_bottom - grid_top) // 6
    kicker_f = font(SANS_BOLD, 18)
    deck_f = font(SANS, 26)
    print("masthead: title_bottom", title_bottom, "date_bottom", date_bottom,
          "grid_top", grid_top, "row_h", row_h)

    for idx, (headline, deck) in enumerate(STORIES):
        col = idx % 3
        row = idx // 3
        x0 = margin + col * (col_w + gutter)
        y0 = grid_top + row * row_h
        pad = 6
        tx = x0 + pad
        text_w = col_w - 2 * pad
        y = y0 + 3

        # kicker (18px, caps/digits only, no descenders)
        y += draw_ink(d, tx, y, "21 NOV", kicker_f, RED) + 4
        # headline, fitted to two lines, complete -- never truncated
        hf, hlines, hsize = fit_headline(d, headline, text_w)
        assert len(hlines) <= 2, f"headline {idx+1} needs {len(hlines)} lines"
        for line in hlines:
            y += draw_ink(d, tx, y, line, hf, INK) + 4
        y += 1  # extra gap before the deck
        # deck, 26px, at most two lines
        dlines = wrap(d, deck, deck_f, text_w)
        assert len(dlines) <= 2, f"deck {idx+1} needs {len(dlines)} lines"
        for line in dlines:
            y += draw_ink(d, tx, y, line, deck_f, (40, 40, 40)) + 4
        content_h = y - 4 - y0
        assert content_h <= row_h - 4, f"cell {idx+1} overflow: {content_h} > {row_h - 4}"
        print(f"cell {idx+1:2d} headline {hsize}px {len(hlines)} lines,"
              f" deck {len(dlines)} lines, content {content_h}px / {row_h}px")

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
