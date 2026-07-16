from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "images"
FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def rounded(draw, xy, fill, outline=None, radius=7, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


PRODUCTS = [
    {
        "id": "chatgpt",
        "accent": "#0B6B52",
        "soft": "#E7F3EF",
        "eyebrow": "OPENAI / CHATGPT",
        "title": "ChatGPT Plus / Pro",
        "subtitle": "订阅 · 付款失败 · 续费 · Free 状态",
        "topics": ["Plus 自动充值", "5x / 20x Pro", "已付款仍是 Free"],
    },
    {
        "id": "grok",
        "accent": "#1F2933",
        "soft": "#E9ECEF",
        "eyebrow": "XAI / GROK",
        "title": "SuperGrok",
        "subtitle": "充值 · User ID · Grok Build · Grok 4.5",
        "topics": ["SuperGrok 充值", "Grok User ID", "登录与 403"],
    },
    {
        "id": "claude",
        "accent": "#A05235",
        "soft": "#F4EAE6",
        "eyebrow": "ANTHROPIC / CLAUDE",
        "title": "Claude Pro / Max",
        "subtitle": "订阅 · User ID · 付款报错 · Claude Code",
        "topics": ["Pro / Max 选择", "银行卡被拒", "Claude Code"],
    },
    {
        "id": "gemini",
        "accent": "#176D84",
        "soft": "#E7F1F4",
        "eyebrow": "GOOGLE / GEMINI",
        "title": "Gemini / Google AI",
        "subtitle": "套餐 · 付款 · 权益 · Google Play",
        "topics": ["自有账号升级", "Gemini 专属账号", "权益未生效"],
    },
]


def draw_product(product):
    image = Image.new("RGB", (1200, 630), "#F7F9F8")
    draw = ImageDraw.Draw(image)
    accent = product["accent"]
    soft = product["soft"]

    draw.rectangle((0, 0, 18, 630), fill=accent)
    draw.text((74, 58), "CHONGGROK · KNOWLEDGE HUB", font=font(24, True), fill=accent)
    draw.text((74, 122), product["eyebrow"], font=font(23, True), fill="#52615C")
    draw.text((74, 178), product["title"], font=font(58, True), fill="#101916")
    draw.text((74, 266), product["subtitle"], font=font(28), fill="#4F5F59")

    top = 354
    for index, topic in enumerate(product["topics"]):
        x = 74 + index * 354
        rounded(draw, (x, top, x + 320, top + 112), fill="#FFFFFF", outline="#CED9D4")
        draw.rectangle((x, top, x + 7, top + 112), fill=accent)
        draw.text((x + 28, top + 22), f"0{index + 1}", font=font(18, True), fill=accent)
        draw.text((x + 28, top + 56), topic, font=font(23, True), fill="#18231F")

    rounded(draw, (74, 510, 1126, 570), fill=soft, outline=None)
    draw.text((102, 526), "结构清晰 · 官方事实 · 报错排查 · 非零风险说明", font=font(22, True), fill=accent)
    image.save(OUTPUT / f"product-preview-{product['id']}.png", optimize=True)


def draw_social_preview():
    image = Image.new("RGB", (1200, 630), "#F7F9F8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 20, 630), fill="#0B6B52")
    draw.text((66, 58), "CHONGGROK KNOWLEDGE HUB", font=font(24, True), fill="#0B6B52")
    draw.text((66, 116), "AI 会员订阅", font=font(58, True), fill="#101916")
    draw.text((66, 184), "与付款排障指南", font=font(58, True), fill="#101916")
    draw.text((66, 282), "搜索问题 · 进入产品知识库 · 回官方页面验收", font=font(25), fill="#53625D")

    positions = [(66, 382), (336, 382), (606, 382), (876, 382)]
    for product, (x, y) in zip(PRODUCTS, positions):
        rounded(draw, (x, y, x + 236, y + 150), fill="#FFFFFF", outline="#CED9D4")
        draw.rectangle((x, y, x + 7, y + 150), fill=product["accent"])
        draw.text((x + 24, y + 25), product["eyebrow"].split(" / ")[-1], font=font(17, True), fill=product["accent"])
        product_name = product["title"].replace(" / Google AI", "")
        draw.text((x + 24, y + 62), product_name, font=font(24, True), fill="#14201D")
        draw.text((x + 24, y + 111), "订阅与排障", font=font(17), fill="#5D6B66")

    image.save(OUTPUT / "social-preview.png", optimize=True)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for item in PRODUCTS:
        draw_product(item)
    draw_social_preview()
    print("Generated 4 product previews and social-preview.png")
