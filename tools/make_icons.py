"""PWA icons (192/512 + maskable-512) for 문서 변환기 · PDF↔이미지.
Dark nav tile + warm amber page-and-arrows glyph, matching the app's dark tone
but distinct from the blue (링크 깔끔이) and green (사진 정보 지우개) sets.
"""
from PIL import Image, ImageDraw, ImageFilter

BG = (11, 14, 18)            # #0b0e12 app background
BG_GLOW = (56, 38, 25)       # warm top glow
ACCENT = (255, 161, 74)      # #ffa14a
ACCENT_DEEP = (240, 121, 41)  # #f07929
PAPER = (233, 239, 246)      # #e9eff6
WORK = 1600


def background(size):
    grad = Image.new("RGB", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        f = (1 - t) ** 1.7
        gd.line([(0, y), (size, y)], fill=tuple(
            int(BG_GLOW[i] * f + BG[i] * (1 - f)) for i in range(3)
        ))
    return grad


def glyph(size, scale):
    """Rounded 'sheet' outline with two opposing arrows inside (PDF <-> image)."""
    L = WORK
    layer = Image.new("L", (L, L), 0)
    d = ImageDraw.Draw(layer)

    # sheet: x 0.275..0.725, y 0.135..0.865 (scaled about the centre)
    def sx(v):
        return 0.5 + (v - 0.5) * scale

    x0, x1 = sx(0.275) * L, sx(0.725) * L
    y0, y1 = sx(0.145) * L, sx(0.855) * L
    stroke = 0.036 * scale * L
    d.rounded_rectangle([x0, y0, x1, y1], radius=0.075 * scale * L,
                        outline=255, width=int(round(stroke)))

    # text lines
    lw = int(round(stroke * 0.62))
    for i, (yy, xe) in enumerate(((0.285, 0.60), (0.355, 0.655))):
        d.line([(sx(0.355) * L, sx(yy) * L), (sx(xe) * L, sx(yy) * L)], fill=255, width=lw)

    # two opposing arrows in the lower half
    aw = int(round(stroke * 1.05))
    head = 0.055 * scale * L
    left = sx(0.355) * L
    right = sx(0.645) * L

    ya = sx(0.50) * L
    d.line([(left, ya), (right - head * 0.45, ya)], fill=255, width=aw)
    d.polygon([(right, ya), (right - head, ya - head * 0.85), (right - head, ya + head * 0.85)], fill=255)

    yb = sx(0.625) * L
    d.line([(left + head * 0.45, yb), (right, yb)], fill=255, width=aw)
    d.polygon([(left, yb), (left + head, yb - head * 0.85), (left + head, yb + head * 0.85)], fill=255)

    # three-dot "page count" row
    r = 0.019 * scale * L
    for k, xx in enumerate((0.365, 0.5, 0.635)):
        cy = sx(0.745) * L
        d.ellipse([sx(xx) * L - r, cy - r, sx(xx) * L + r, cy + r], fill=255)

    return layer.resize((size, size), Image.LANCZOS)


def make(size, scale=1.0):
    img = background(size).convert("RGBA")
    g = glyph(size, scale)

    glow = g.filter(ImageFilter.GaussianBlur(radius=size * 0.045)).point(lambda v: int(v * 0.55))
    img.paste(Image.new("RGBA", (size, size), ACCENT + (255,)), (0, 0), glow)

    grad = Image.new("RGB", (size, size))
    gd = ImageDraw.Draw(grad)
    for y in range(size):
        t = y / size
        gd.line([(0, y), (size, y)], fill=tuple(
            int(PAPER[i] * (1 - t) + ACCENT[i] * t) for i in range(3)
        ))
    img.paste(grad, (0, 0), g)
    return img


if __name__ == "__main__":
    make(512, 1.06).save("work/pdf-image-repo/icon-512.png", optimize=True)
    make(192, 1.06).save("work/pdf-image-repo/icon-192.png", optimize=True)
    make(512, 0.78).save("work/pdf-image-repo/icon-maskable-512.png", optimize=True)
    print("icons written")
