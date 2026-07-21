from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "downloads" / "labs" / "codex-dream-skin-galaxy-static.jpg"
OUTPUT = ROOT / "assets" / "images" / "labs" / "codex-dream-skin-windows-social.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    family = "msyhbd.ttc" if bold else "msyh.ttc"
    return ImageFont.truetype(f"C:/Windows/Fonts/{family}", size=size)


def main() -> None:
    with Image.open(SOURCE).convert("RGB") as source:
        ratio = 1200 / 630
        source_ratio = source.width / source.height
        if source_ratio > ratio:
            width = round(source.height * ratio)
            left = (source.width - width) // 2
            source = source.crop((left, 0, left + width, source.height))
        else:
            height = round(source.width / ratio)
            top = (source.height - height) // 2
            source = source.crop((0, top, source.width, top + height))
        canvas = source.resize((1200, 630), Image.Resampling.LANCZOS)

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, 760, 630), fill=(3, 12, 30, 214))
    draw.rectangle((0, 0, 22, 630), fill=(11, 107, 82, 255))

    draw.text((72, 64), "CHONGGROK TECHNICAL LAB", font=font(24, True), fill="#75D6BE")
    draw.text((72, 148), "Windows Codex Desktop", font=font(54, True), fill="#FFFFFF")
    draw.text((72, 224), "动态换肤实测教程", font=font(58, True), fill="#FFFFFF")
    draw.text((72, 332), "安装 · CDP 验证 · 安全边界 · 完整恢复", font=font(27), fill="#D8E9F2")
    draw.rounded_rectangle((72, 440, 610, 514), radius=7, fill=(255, 255, 255, 28), outline=(117, 214, 190, 150), width=2)
    draw.text((98, 461), "Pinned source · Real failure records · Restore tested", font=font(20), fill="#E7F7F2")
    draw.text((72, 568), "he20000405-pixel.github.io/labs/", font=font(18), fill="#AABFCA")

    result = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUTPUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
