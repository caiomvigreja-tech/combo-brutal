from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

RED = (224, 32, 32)
ORANGE = (255, 109, 15)
WHITE = (245, 245, 245)
MUTED = (176, 176, 176)
BLACK = (5, 5, 5)

FONT_DISPLAY = "/System/Library/Fonts/Supplemental/Impact.ttf"
FONT_DISPLAY_2 = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
FONT_BODY = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BODY_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def cover(path):
    return Image.open(ROOT / path).convert("RGBA")


def fit_fill(img, size):
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def paste_rounded(base, img, box, radius=28, shadow=True):
    x, y = box
    if shadow:
        shadow_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sm = rounded_mask(img.size, radius)
        shadow_img.putalpha(sm)
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(22))
        shadow_fill = Image.new("RGBA", img.size, (0, 0, 0, 150))
        shadow_fill.putalpha(shadow_img.getchannel("A"))
        base.alpha_composite(shadow_fill, (x + 18, y + 22))
    mask = rounded_mask(img.size, radius)
    base.paste(img, (x, y), mask)


def paste_rotated(base, img, center, angle, radius=28, scale=1.0):
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    mask = rounded_mask(img.size, radius)
    rounded = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rounded.paste(img, (0, 0), mask)
    rotated = rounded.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
    x = int(center[0] - rotated.width / 2)
    y = int(center[1] - rotated.height / 2)
    shadow = Image.new("RGBA", rotated.size, (0, 0, 0, 150))
    shadow.putalpha(rotated.getchannel("A").filter(ImageFilter.GaussianBlur(24)))
    base.alpha_composite(shadow, (x + 18, y + 24))
    base.alpha_composite(rotated, (x, y))


def linear_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGBA", size, top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(4))
        for x in range(w):
            px[x, y] = color
    return img


def radial_glow(size, center, radius, color):
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    px = img.load()
    cx, cy = center
    for y in range(h):
        for x in range(w):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if d < radius:
                a = int(color[3] * (1 - d / radius) ** 2)
                px[x, y] = (*color[:3], a)
    return img.filter(ImageFilter.GaussianBlur(18))


def draw_text(draw, xy, text, fnt, fill, anchor=None, align="left"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor, align=align)


def text_center(draw, y, text, fnt, fill, width):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text(((width - (bbox[2] - bbox[0])) / 2, y), text, font=fnt, fill=fill)


def build_course_card(src, out, title_lines, accent_line=None, crop=(520, 640)):
    raw = cover(src)
    bg = linear_gradient(crop, (8, 8, 8, 255), (18, 3, 3, 255))
    bg.alpha_composite(radial_glow(crop, (crop[0] // 2, crop[1] // 2), 430, (224, 32, 32, 90)))

    card = fit_fill(raw, crop)
    bg.alpha_composite(card)

    overlay_top = linear_gradient(crop, (0, 0, 0, 160), (0, 0, 0, 0))
    overlay = linear_gradient(crop, (0, 0, 0, 0), (0, 0, 0, 210))
    bg.alpha_composite(overlay_top)
    bg.alpha_composite(overlay)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((24, 24, 188, 58), radius=6, fill=(224, 32, 32, 235))
    draw_text(d, (106, 31), "INCLUSO", font(FONT_BODY_BOLD, 18), WHITE, anchor="ma")
    draw_text(d, (32, 86), "UNIVERSIDADE SISV", font(FONT_BODY_BOLD, 15), MUTED)

    y = crop[1] - 150
    for i, line in enumerate(title_lines):
        fill = RED if accent_line and line == accent_line else WHITE
        text_center(d, y + i * 57, line, font(FONT_DISPLAY, 52), fill, crop[0])
    bg.save(ASSETS / out)


def build_bonus(src_generated):
    source = cover(src_generated)
    canvas = Image.new("RGBA", (720, 900), (4, 4, 4, 255))
    canvas.alpha_composite(radial_glow(canvas.size, (360, 440), 540, (224, 32, 32, 92)))
    visual = fit_fill(source, (720, 900))
    canvas.alpha_composite(visual)
    shade = linear_gradient((720, 900), (0, 0, 0, 35), (0, 0, 0, 205))
    canvas.alpha_composite(shade)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((42, 42, 238, 80), radius=6, fill=(224, 32, 32, 235))
    draw_text(d, (140, 50), "MASTERCLASS", font(FONT_BODY_BOLD, 20), WHITE, anchor="ma")
    draw_text(d, (54, 690), "NOVA ERA DA", font(FONT_DISPLAY_2, 64), WHITE)
    draw_text(d, (54, 752), "GESTÃO DE", font(FONT_DISPLAY_2, 64), WHITE)
    draw_text(d, (54, 814), "TRÁFEGO", font(FONT_DISPLAY_2, 74), ORANGE)
    canvas.save(ASSETS / "bonus-trafego-ai.png")


def build_hero():
    w, h = 1440, 900
    canvas = linear_gradient((w, h), (5, 5, 5, 255), (18, 6, 4, 255))
    canvas.alpha_composite(radial_glow((w, h), (720, 450), 720, (224, 32, 32, 125)))
    canvas.alpha_composite(radial_glow((w, h), (720, 180), 520, (255, 109, 15, 62)))
    d = ImageDraw.Draw(canvas)

    fechamento = fit_fill(cover("assets/curso-fechamento-brutal.png"), (470, 580))
    persuasao = fit_fill(cover("assets/curso-persuasao-brutal.png"), (330, 406))
    metas = fit_fill(cover("assets/curso-metas-comerciais.png"), (330, 406))

    paste_rotated(canvas, persuasao, (350, 508), -9, 26)
    paste_rotated(canvas, metas, (1090, 508), 9, 26)
    paste_rotated(canvas, fechamento, (720, 470), 0, 30)

    d.rounded_rectangle((78, 62, 350, 110), radius=8, fill=(224, 32, 32, 235))
    draw_text(d, (214, 72), "3 TREINAMENTOS", font(FONT_BODY_BOLD, 24), WHITE, anchor="ma")
    d.rounded_rectangle((1086, 720, 1346, 778), radius=8, fill=(8, 8, 8, 230), outline=(224, 32, 32, 180), width=2)
    draw_text(d, (1216, 737), "ACESSO IMEDIATO", font(FONT_BODY_BOLD, 22), MUTED, anchor="ma")

    canvas.save(ASSETS / "combo-brutal-hero.png")


def main():
    build_course_card(
        "assets/source-fechamento.png",
        "curso-fechamento-brutal.png",
        ["FECHAMENTO", "BRUTAL"],
        "BRUTAL",
    )
    build_course_card(
        "assets/source-persuasao.png",
        "curso-persuasao-brutal.png",
        ["PERSUASÃO", "BRUTAL"],
        "BRUTAL",
    )
    build_course_card(
        "assets/source-metas.png",
        "curso-metas-comerciais.png",
        ["METAS", "COMERCIAIS"],
    )
    build_bonus("assets/source-bonus-trafego.png")
    build_hero()


if __name__ == "__main__":
    main()
