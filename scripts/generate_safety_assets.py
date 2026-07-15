from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
DOWNLOADS = ROOT / "assets" / "downloads"
IMAGES.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)

CN = Path(r"C:\Windows\Fonts\msyh.ttc")
CN_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
EN = Path(r"C:\Windows\Fonts\arial.ttf")
EN_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

INK, MUTED, GREEN = "#14201d", "#52635d", "#0b6b52"
PALE, LINE, AMBER = "#edf8f4", "#cbdad5", "#a45b10"


def pil_font(path, size):
    return ImageFont.truetype(str(path), size)


def wrap(draw, text, face, max_width):
    words = list(text) if any("\u4e00" <= c <= "\u9fff" for c in text) else text.split()
    lines, current = [], ""
    for word in words:
        separator = "" if len(word) == 1 and words == list(text) else " "
        candidate = current + (separator if current else "") + word
        if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def make_social():
    image = Image.new("RGB", (1200, 630), "#f7faf8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 28, 630), fill=GREEN)
    draw.text((82, 72), "CHONGGROK · REUSABLE RESOURCE", fill=GREEN, font=pil_font(EN_BOLD, 25))
    draw.text((82, 145), "AI 会员订阅安全", fill=INK, font=pil_font(CN_BOLD, 66))
    draw.text((82, 230), "与验收清单", fill=INK, font=pil_font(CN_BOLD, 66))
    draw.text((82, 345), "ChatGPT · Grok · Claude · Gemini", fill=MUTED, font=pil_font(EN_BOLD, 31))
    draw.rounded_rectangle((82, 430, 1115, 535), radius=12, fill=PALE, outline=LINE, width=2)
    draw.text((112, 457), "认清购买入口  ·  只交最小资料  ·  回官方页面验收", fill=GREEN, font=pil_font(CN_BOLD, 29))
    image.save(IMAGES / "ai-membership-safety-checklist-social.png", quality=95)


def make_infographic(language):
    zh = language == "zh"
    image = Image.new("RGB", (1200, 1600), "#f8faf9")
    draw = ImageDraw.Draw(image)
    regular = CN if zh else EN
    bold = CN_BOLD if zh else EN_BOLD
    draw.rectangle((0, 0, 1200, 18), fill=GREEN)
    draw.text((70, 55), "CHONGGROK · 2026", fill=GREEN, font=pil_font(EN_BOLD, 24))
    title = "AI 会员订阅安全与验收清单" if zh else "AI Membership Safety Checklist"
    draw.text((70, 112), title, fill=INK, font=pil_font(bold, 54))
    subtitle = "ChatGPT · Grok · Claude · Gemini" if zh else "ChatGPT · Grok · Claude · Gemini"
    draw.text((70, 192), subtitle, fill=MUTED, font=pil_font(regular, 26))
    blocks = [
        ("01  付款前" if zh else "01  BEFORE PAYMENT", [
            "确认自己的账号可以正常登录" if zh else "Confirm the account can sign in",
            "检查已有会员、试用和待处理订单" if zh else "Check plans, trials and pending orders",
            "记录网页、Apple、Google Play 或第三方入口" if zh else "Record the web, Apple, Google Play or third-party channel",
        ]),
        ("02  最小资料" if zh else "02  MINIMUM DATA", [
            "不交密码、验证码或恢复码" if zh else "Never share passwords, codes or recovery data",
            "session 和 User ID 也不能公开" if zh else "Do not publish sessions or User IDs",
            "Gemini 资料由客服逐单确认" if zh else "Gemini requirements are confirmed case by case",
        ]),
        ("03  付款后" if zh else "03  AFTER PAYMENT", [
            "区分预授权、收据和有效订阅" if zh else "Separate authorizations, receipts and entitlements",
            "回原购买入口检查订单状态" if zh else "Check the original billing channel",
            "回官方产品页面验收计划" if zh else "Verify the plan on the official product page",
        ]),
        ("04  没生效" if zh else "04  IF IT IS MISSING", [
            "停止重复付款，保存订单和时间" if zh else "Stop; do not pay again",
            "确认原购买账号和登录方式" if zh else "Confirm the purchasing account and sign-in method",
            "账单问题与权益问题找正确支持方" if zh else "Send billing and entitlement issues to the right provider",
        ]),
    ]
    y = 285
    for heading, bullets in blocks:
        draw.rounded_rectangle((70, y, 1130, y + 235), radius=14, fill="white", outline=LINE, width=2)
        draw.text((105, y + 28), heading, fill=GREEN, font=pil_font(bold, 30))
        by = y + 88
        for item in bullets:
            draw.ellipse((108, by + 8, 120, by + 20), fill=AMBER)
            draw.text((142, by), item, fill=INK, font=pil_font(regular, 27))
            by += 48
        y += 255
    draw.rounded_rectangle((70, 1320, 1130, 1475), radius=14, fill=PALE, outline="#9fc9bb", width=2)
    warning = "不要密码不等于零风险；已有扣款或待处理交易时不要重复购买。" if zh else "Passwordless does not mean risk-free. Do not repurchase while a charge is complete or pending."
    face = pil_font(bold, 30)
    for index, line in enumerate(wrap(draw, warning, face, 960)):
        draw.text((110, 1352 + index * 44), line, fill=GREEN, font=face)
    footer = "he20000405-pixel.github.io/resources/ai-membership-safety-checklist/" if zh else "he20000405-pixel.github.io/en/resources/ai-membership-safety-checklist/"
    draw.text((70, 1530), footer, fill=MUTED, font=pil_font(EN, 22))
    image.save(IMAGES / f"ai-membership-safety-checklist-{language}.png", quality=95)


def make_pdf(language):
    zh = language == "zh"
    regular, bold = ("MSYH", "MSYH-Bold") if zh else ("Arial", "Arial-Bold")
    pdfmetrics.registerFont(TTFont(regular, str(CN if zh else EN)))
    pdfmetrics.registerFont(TTFont(bold, str(CN_BOLD if zh else EN_BOLD)))
    path = DOWNLOADS / f"ai-membership-safety-checklist-{language}.pdf"
    doc = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    margin = 46

    def page_header(number):
        doc.setFillColor(HexColor(GREEN)); doc.rect(0, height - 14, width, 14, stroke=0, fill=1)
        doc.setFont(bold, 10); doc.drawString(margin, height - 38, "CHONGGROK · 2026 AI SUBSCRIPTION SAFETY")
        doc.setFillColor(HexColor(MUTED)); doc.setFont(regular, 8.5)
        doc.drawRightString(width - margin, 25, f"{number} / 2 · he20000405-pixel.github.io")

    def section(y, title, items):
        doc.setFillColor(HexColor(PALE)); doc.roundRect(margin, y - 112, width - margin * 2, 112, 7, stroke=0, fill=1)
        doc.setFillColor(HexColor(GREEN)); doc.setFont(bold, 13); doc.drawString(margin + 16, y - 23, title)
        doc.setFont(regular, 10.2); line_y = y - 46
        for item in items:
            doc.setFillColor(HexColor(AMBER)); doc.circle(margin + 20, line_y + 3, 2.2, stroke=0, fill=1)
            doc.setFillColor(HexColor(INK)); doc.drawString(margin + 31, line_y, item); line_y -= 21
        return y - 128

    page_header(1)
    doc.setFillColor(HexColor(INK)); doc.setFont(bold, 24)
    doc.drawString(margin, height - 83, "AI 会员订阅安全与验收清单" if zh else "AI Membership Safety Checklist")
    doc.setFillColor(HexColor(MUTED)); doc.setFont(regular, 11); doc.drawString(margin, height - 105, "ChatGPT · Grok · Claude · Gemini")
    if zh:
        sections = [
            ("01 付款前", ["确认账号可以登录，并检查已有会员、试用和待处理订单。", "记录购买入口：官方网页、App Store、Google Play 或第三方。", "套餐、价格、额度和地区可用性以官方实时页面为准。"]),
            ("02 最小必要资料", ["不提交密码、邮箱验证码、两步验证码或恢复码。", "session 和 User ID 也不应公开，只在确认的履约流程中提交。", "Gemini 仅处理用户自有账号，资料由客服逐单确认。"]),
            ("03 付款后验收", ["区分银行预授权、正式收据、商店有效订阅和官方权益。", "回原购买入口检查订单，再回官方产品页面核对计划。", "保存订单号、准确时间、付款账号和脱敏后的计划截图。"]),
            ("04 权益未出现", ["停止重复付款，确认原购买账号和登录方式。", "账单未完成联系账单方；账单完成但权益缺失联系产品支持。", "ChongGrok 订单通过原订单记录联系 ChongGrok 售后。"]),
        ]
    else:
        sections = [
            ("01 BEFORE PAYMENT", ["Confirm the account can sign in; check plans, trials and pending orders.", "Record whether billing is web, App Store, Google Play or third-party.", "Use official pages for plans, prices, limits and availability."]),
            ("02 MINIMUM DATA", ["Never share passwords, verification codes or recovery codes.", "Sessions and User IDs should only be used in a verified flow.", "Gemini supports the user's account; requirements are confirmed case by case."]),
            ("03 VERIFY AFTER PAYMENT", ["Separate bank authorizations, receipts, store subscriptions and entitlements.", "Check the original billing channel, then the official product page.", "Keep the order ID, time, purchasing account and a masked plan screen."]),
            ("04 IF THE PLAN IS MISSING", ["Stop and do not pay again; confirm the account and sign-in method.", "Send incomplete charges to billing and missing entitlements to product support.", "Use the original order when contacting ChongGrok about its order."]),
        ]
    y = height - 140
    for title, items in sections:
        y = section(y, title, items)
    doc.setFillColor(HexColor("#fff5f4")); doc.roundRect(margin, 55, width - margin * 2, 54, 7, stroke=0, fill=1)
    doc.setFillColor(HexColor("#8f2f28")); doc.setFont(bold, 10.2)
    warning = "不要密码不等于零风险；已有扣款或待处理交易时不要重复购买。" if zh else "Passwordless is not risk-free. Do not repurchase while a charge is complete or pending."
    doc.drawString(margin + 14, 78, warning); doc.showPage()

    page_header(2); doc.setFillColor(HexColor(INK)); doc.setFont(bold, 18)
    doc.drawString(margin, height - 75, "产品资料与验收边界" if zh else "Product data and verification boundaries")
    rows = [
        ("ChatGPT", "session 敏感；完成后重新登录刷新" if zh else "Sensitive session; sign out and back in afterwards"),
        ("Grok", "User ID 是账号标识，不是登录密码" if zh else "User ID identifies the account; it is not a password"),
        ("Claude", "User ID 是履约标识，不是 Anthropic 订阅要求" if zh else "User ID is a fulfillment identifier, not an Anthropic billing rule"),
        ("Gemini", "仅自有账号；资料由客服逐单确认" if zh else "Own account only; requirements are confirmed case by case"),
    ]
    y = height - 112
    for product, detail in rows:
        doc.setFillColor(HexColor(PALE)); doc.roundRect(margin, y - 54, width - margin * 2, 48, 6, stroke=0, fill=1)
        doc.setFillColor(HexColor(GREEN)); doc.setFont(bold, 11); doc.drawString(margin + 14, y - 26, product)
        doc.setFillColor(HexColor(INK)); doc.setFont(regular, 9.4); doc.drawString(margin + 92, y - 26, detail); y -= 62
    doc.setFont(bold, 14); doc.drawString(margin, y - 5, "售后证据" if zh else "Evidence to keep")
    doc.setFont(regular, 10.2)
    evidence = [
        "产品、套餐、周期和原购买入口" if zh else "Product, plan, term and original billing channel",
        "订单号、收据、交易状态和准确时间" if zh else "Order ID, receipt, transaction status and exact time",
        "当前账号的脱敏标识和官方计划页面" if zh else "Masked account identifier and official plan screen",
        "错误提示、设备环境和已尝试步骤" if zh else "Error message, device environment and attempted steps",
    ]
    ey = y - 31
    for item in evidence:
        doc.circle(margin + 5, ey + 3, 2, stroke=0, fill=1); doc.drawString(margin + 16, ey, item); ey -= 23
    doc.setFillColor(HexColor(PALE)); doc.roundRect(margin, 130, width - margin * 2, 120, 7, stroke=0, fill=1)
    doc.setFillColor(HexColor(GREEN)); doc.setFont(bold, 12)
    doc.drawString(margin + 16, 220, "独立性与风险说明" if zh else "Independence and risk disclosure")
    doc.setFillColor(HexColor(INK)); doc.setFont(regular, 9.2)
    disclosure = [
        "ChongGrok 是独立第三方，与相关 AI 公司不存在隶属或官方合作。" if zh else "ChongGrok is independent and not officially partnered with the AI providers.",
        "套餐、价格、额度、可用性和退款政策以官方实时页面为准。" if zh else "Plans, prices, limits, availability and refunds are controlled by each provider.",
        "完整更新版：he20000405-pixel.github.io/resources/ai-membership-safety-checklist/" if zh else "Updated version: he20000405-pixel.github.io/en/resources/ai-membership-safety-checklist/",
    ]
    dy = 194
    for line in disclosure:
        doc.drawString(margin + 16, dy, line); dy -= 22
    doc.save()


if __name__ == "__main__":
    make_social()
    for lang in ("zh", "en"):
        make_infographic(lang)
        make_pdf(lang)
