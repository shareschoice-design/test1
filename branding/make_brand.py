from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = "/root/.fonts/Montserrat.ttf"
def font(sz, w=b"ExtraBold"):
    f = ImageFont.truetype(F, sz); f.set_variation_by_name(w); return f
RED, CYAN, WHITE = (255, 59, 59), (63, 216, 255), (255, 255, 255)

# logos: crop to the cyan ring so it fills the round avatar, 800x800
for name, crop in [("logo_eye", 0.80), ("logo_claw", 0.82)]:
    im = Image.open(f"src/{name}.png").convert("RGB")
    w, h = im.size; c = int(w * crop); o = (w - c) // 2
    im.crop((o, o, o + c, o + c)).resize((800, 800), Image.LANCZOS).save(f"{name}_800.png")

# banner 2560x1440 with text in the 1546x423 safe area
bg = Image.open("src/banner_bg.png").convert("RGB").resize((2560, 1440), Image.LANCZOS)
cx, cy = 1280, 720
# darken centre band for legibility
shade = Image.new("L", bg.size, 0); ImageDraw.Draw(shade).rounded_rectangle((520, 540, 2040, 900), 80, fill=150)
shade = shade.filter(ImageFilter.GaussianBlur(60))
bg = Image.composite(Image.new("RGB", bg.size, (6, 8, 12)), bg, shade)
layer = Image.new("RGBA", bg.size, (0, 0, 0, 0)); glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
d, g = ImageDraw.Draw(layer), ImageDraw.Draw(glow)
ft = font(150); a, b = "WILD ", "REWIND"
wa, wb = ft.getlength(a), ft.getlength(b); x = cx - (wa + wb) / 2; y = cy + 10
d.text((x, y), a, font=ft, fill=WHITE, anchor="ls")
g.text((x + wa, y), b, font=ft, fill=RED + (255,), anchor="ls"); d.text((x + wa, y), b, font=ft, fill=RED, anchor="ls")
ft2 = font(52, b"SemiBold"); tag = "Every wild moment has a backstory."
d.text((cx, y + 85), tag, font=ft2, fill=WHITE, anchor="ms")
ft3 = font(34, b"Bold"); sub = "NEW REWIND EVERY DAY"
d.text((cx, y + 150), sub, font=ft3, fill=CYAN, anchor="ms")
g = glow.filter(ImageFilter.GaussianBlur(26))
out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(bg.convert("RGBA"), g), g), layer)
out.convert("RGB").save("banner_2560x1440.png")
# preview with safe areas marked (not for upload)
p = out.convert("RGB").copy(); pd = ImageDraw.Draw(p)
pd.rectangle((507, 508, 2053, 931), outline=(255, 255, 0), width=4)   # all devices
pd.rectangle((0, 508, 2560, 931), outline=(0, 255, 0), width=2)      # desktop strip
p.resize((1280, 720)).save("/tmp/claude-0/-home-user-test1/3f5d5508-2172-59cb-b461-77d18d886728/scratchpad/banner_prev.jpg")
