"""Renders every post's photos per platform with the Mitchell's logo plate on the photo.

Run: python3 scripts/render_media.py [--force]
Output: media/rendered/<post-id>/<platform>-<n>.jpg plus media/rendered/manifest.json

Sizes (playbook): Instagram 1080x1350; Facebook keeps squares 1080x1080 and landscapes 1200x800;
Google Business Profile 1200x900.
Logo: Mitchell's wordmark is wide, so it sits on a white rounded plate with a thin red edge
(easy to read on any photo). The plate goes in the calmest of eight spots, unless the
catalog pins `logoSpot`. Photos with `hasLogo` get no plate.
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RED = (224, 43, 32)
LOGO = Image.open(os.path.join(ROOT, "media/logos/mitchells-logo-wide.png")).convert("RGBA")
LOGO = LOGO.crop(LOGO.getbbox())
PLATE_W = 0.44          # plate width as a share of the frame width
SPOTS = ["top-left", "top-right", "bottom-left", "bottom-right", "top-center", "bottom-center", "middle-left", "middle-right"]
SIZES = {"instagram": (1080, 1350), "gbp": (1200, 900)}


def fb_size(w, h):
    r = w / h
    return (1080, 1080) if r < 1.15 else (1200, round(1200 / min(r, 1.91)))


def cover(im, size):
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2
    out = im.crop((l, t, l + tw, t + th))
    return out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)) if s > 1.05 else out


def contain(im, size):
    tw, th = size
    bg = Image.open(os.path.join(ROOT, "media/website/mitchells-bg-1500x1000-1.jpg")).convert("RGB")
    bg = cover(bg, size)
    s = min(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    bg.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
    return bg, ((tw - im.width) // 2, (th - im.height) // 2, im.width, im.height)


def plate(width):
    pad_x, pad_y = round(width * 0.06), round(width * 0.05)
    lw = width - 2 * pad_x
    logo = LOGO.resize((lw, round(LOGO.height * lw / LOGO.width)), Image.LANCZOS)
    h = logo.height + 2 * pad_y
    p = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    r = round(h * 0.22)
    d.rounded_rectangle((0, 0, width - 1, h - 1), r, fill=(255, 255, 255, 245), outline=RED, width=max(3, width // 110))
    p.alpha_composite(logo, (pad_x, pad_y))
    return p


def spot_box(spot, area, pw, ph):
    ax, ay, aw, ah = area
    m = round(aw * 0.035)
    x = {"left": ax + m, "right": ax + aw - pw - m, "center": ax + (aw - pw) // 2}
    y = {"top": ay + m, "bottom": ay + ah - ph - m, "middle": ay + (ah - ph) // 2}
    v, h = spot.split("-")
    return x[h], y[v]


def busyness(img, box):
    region = img.crop(box).convert("L")
    edges = region.filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(region).stddev[0] + 2 * ImageStat.Stat(edges).mean[0]


def place(img, area, pin):
    pw = round(area[2] * PLATE_W)
    pl = plate(pw)
    spots = [pin] if pin else SPOTS
    scored = []
    for s in spots:
        x, y = spot_box(s, area, pl.width, pl.height)
        scored.append((busyness(img, (x, y, x + pl.width, y + pl.height)), s, x, y))
    _, s, x, y = min(scored)
    out = img.convert("RGBA")
    shadow = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x + 4, y + 6, x + pl.width + 4, y + pl.height + 6), round(pl.height * 0.22), fill=(0, 0, 0, 90))
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
    out.alpha_composite(pl, (x, y))
    return out.convert("RGB"), s


def render(photo, size):
    im = Image.open(os.path.join(ROOT, photo["file"])).convert("RGB")
    if photo.get("fit") == "contain":
        img, area = contain(im, size)
    else:
        img, area = cover(im, size), (0, 0) + size
    if photo.get("hasLogo"):
        return img, None
    return place(img, area, photo.get("logoSpot"))


def main():
    force = "--force" in sys.argv
    cat = {c["id"]: c for c in json.load(open(os.path.join(ROOT, "media/catalog.json")))["photos"]}
    manifest = {}
    for wf in sorted(glob.glob(os.path.join(ROOT, "content/weeks/*.json"))):
        for post in json.load(open(wf))["posts"]:
            outdir = os.path.join(ROOT, "media/rendered", post["id"])
            os.makedirs(outdir, exist_ok=True)
            entry = manifest[post["id"]] = {}
            for platform in post["variants"]:
                ids = post["variants"][platform].get("media") or post["media"]
                files = []
                for n, mid in enumerate(ids, 1):
                    photo = cat[mid]
                    size = fb_size(*Image.open(os.path.join(ROOT, photo["file"])).size) if platform == "facebook" else SIZES[platform]
                    path = os.path.join(outdir, f"{platform}-{n}.jpg")
                    if force or not os.path.exists(path):
                        img, spot = render(photo, size)
                        img.save(path, quality=88, optimize=True)
                    files.append(os.path.relpath(path, ROOT))
                entry[platform] = files
    json.dump(manifest, open(os.path.join(ROOT, "media/rendered/manifest.json"), "w"), indent=1)
    print(sum(len(f) for e in manifest.values() for f in e.values()), "images rendered")


if __name__ == "__main__":
    main()
