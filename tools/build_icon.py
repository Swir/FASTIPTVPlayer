from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
PNG = ASSETS / "fastiptv.png"
ICO = ASSETS / "fastiptv.ico"


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (512, 512), (6, 17, 30, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, 494, 494), radius=105, fill=(10, 34, 55, 255), outline=(79, 184, 255, 255), width=12)
    draw.rounded_rectangle((82, 104, 430, 350), radius=30, fill=(11, 30, 49, 255), outline=(139, 215, 255, 255), width=14)
    draw.polygon([(220, 170), (220, 286), (318, 228)], fill=(79, 184, 255, 255))
    draw.line((176, 398, 336, 398), fill=(139, 215, 255, 255), width=18)
    draw.line((256, 350, 256, 398), fill=(139, 215, 255, 255), width=18)
    draw.ellipse((379, 121, 415, 157), fill=(106, 255, 194, 255))
    image.save(PNG)
    image.save(ICO, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated {PNG.name} and {ICO.name}")


if __name__ == "__main__":
    build()
