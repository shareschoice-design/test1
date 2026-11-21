"""Render a short-form caption overlay (transparent PNG, 1080x1920).
Style: bold uppercase Montserrat, white text with highlighted keyword(s) in red/coral glow,
soft dark shadow for readability on any footage."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FONT = "/root/.fonts/Montserrat.ttf"
W, H = 1080, 1920
WHITE = (255, 255, 255, 255)
ACCENT = (255, 59, 59, 255)       # red/coral highlight
GLOW = (255, 40, 40, 255)

def font(size, weight=b"ExtraBold"):
    f = ImageFont.truetype(FONT, size)
    try: f.set_variation_by_name(weight)
    except Exception: pass
    return f

def render(words, highlight, out, size=64, y=None, bg=None):
    """words: caption text; highlight: set of word indexes to colour accent."""
    toks = words.upper().split()
    maxw = W * 0.82
    # split into at most 2 balanced lines if needed, then shrink to fit
    def lines_for(f):
        sp = f.getlength(" ")
        full = sum(f.getlength(t) for t in toks) + sp * (len(toks) - 1)
        if full <= maxw or len(toks) < 2: return [list(range(len(toks)))]
        best = None
        for k in range(1, len(toks)):
            a = sum(f.getlength(t) for t in toks[:k]) + sp*(k-1)
            b = sum(f.getlength(t) for t in toks[k:]) + sp*(len(toks)-k-1)
            if best is None or max(a, b) < best[0]: best = (max(a, b), k)
        k = best[1]
        return [list(range(k)), list(range(k, len(toks)))]
    while True:
        f = font(size)
        lines = lines_for(f)
        sp = f.getlength(" ")
        lw = [sum(f.getlength(toks[i]) for i in ln) + sp*(len(ln)-1) for ln in lines]
        if max(lw) <= maxw or size <= 36: break
        size -= 2
    lh = size * 1.18
    y = H * 0.52 if y is None else y
    y -= lh * (len(lines) - 1) / 2
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0)) if bg is None else bg.convert("RGBA").resize((W, H))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    text = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds, dg, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(glow), ImageDraw.Draw(text)
    for li, (ln, w) in enumerate(zip(lines, lw)):
        x = (W - w) / 2
        yy = y + li * lh
        for i in ln:
            t = toks[i]; hl = i in highlight
            ds.text((x, yy + 4), t, font=f, fill=(0, 0, 0, 230), anchor="ls")
            if hl: dg.text((x, yy), t, font=f, fill=GLOW, anchor="ls")
            dt.text((x, yy), t, font=f, fill=ACCENT if hl else WHITE, anchor="ls",
                    stroke_width=1, stroke_fill=(0, 0, 0, 90))
            x += f.getlength(t) + sp
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    g1, g2 = glow.filter(ImageFilter.GaussianBlur(22)), glow.filter(ImageFilter.GaussianBlur(8))
    glow = Image.alpha_composite(Image.alpha_composite(g1, g1), g2)
    for layer in (shadow, shadow, glow, text):
        base = Image.alpha_composite(base, layer)
    base.save(out)

if __name__ == "__main__":
    text, hl, out = sys.argv[1], {int(i) for i in sys.argv[2].split(",") if i}, sys.argv[3]
    bg = Image.open(sys.argv[4]) if len(sys.argv) > 4 else None
    render(text, hl, out, bg=bg)
