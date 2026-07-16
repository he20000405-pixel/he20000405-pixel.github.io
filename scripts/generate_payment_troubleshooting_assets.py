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
OUTREACH_ASSETS = ROOT.parents[1] / "outreach" / "assets"
IMAGES.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)
OUTREACH_ASSETS.mkdir(parents=True, exist_ok=True)

CN = Path(r"C:\Windows\Fonts\msyh.ttc")
CN_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
EN = Path(r"C:\Windows\Fonts\arial.ttf")
EN_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

INK = "#13201c"
MUTED = "#52635d"
GREEN = "#0b6b52"
PALE = "#edf8f4"
LINE = "#c6d8d2"
AMBER = "#a45b10"
RED = "#96352e"
WHITE = "#ffffff"
BG = "#f7faf8"


def font(path, size):
    return ImageFont.truetype(str(path), size)


def wrap_text(draw, text, face, width):
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        tokens = list(text)
        joiner = ""
    else:
        tokens = text.split()
        joiner = " "
    lines = []
    current = ""
    for token in tokens:
        candidate = current + (joiner if current else "") + token
        if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = token
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, xy, text, face, fill, width, spacing):
    x, y = xy
    lines = wrap_text(draw, text, face, width)
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += spacing
    return y


def make_social(language):
    zh = language == "zh"
    image = Image.new("RGB", (1200, 630), BG)
    draw = ImageDraw.Draw(image)
    regular = CN if zh else EN
    bold = CN_BOLD if zh else EN_BOLD

    draw.rectangle((0, 0, 30, 630), fill=GREEN)
    draw.text((82, 62), "CHONGGROK · TROUBLESHOOTING RESOURCE", fill=GREEN, font=font(EN_BOLD, 24))
    if zh:
        draw.text((82, 132), "AI 订阅付款", fill=INK, font=font(bold, 68))
        draw.text((82, 220), "排障决策树", fill=INK, font=font(bold, 68))
        subtitle = "已扣款未生效 · 仍显示 Free · 续费失败"
        steps = ["停止重复付款", "确认购买入口", "核对账号与权益"]
    else:
        draw.text((82, 138), "AI Subscription Payment", fill=INK, font=font(bold, 58))
        draw.text((82, 214), "Troubleshooting", fill=INK, font=font(bold, 58))
        subtitle = "Charged but Free · Renewal failed · Duplicate plans"
        steps = ["STOP", "TRACE BILLING", "VERIFY ENTITLEMENT"]
    draw.text((82, 330), subtitle, fill=MUTED, font=font(regular, 29))

    x = 82
    for index, step in enumerate(steps, 1):
        box_width = 320 if zh else 330
        draw.rounded_rectangle((x, 430, x + box_width, 525), radius=10, fill=WHITE, outline=LINE, width=2)
        draw.ellipse((x + 20, 451, x + 66, 497), fill=GREEN)
        label_face = font(EN_BOLD, 21)
        number_width = draw.textbbox((0, 0), str(index), font=label_face)[2]
        draw.text((x + 43 - number_width / 2, 461), str(index), fill=WHITE, font=label_face)
        draw.text((x + 82, 460 if zh else 457), step, fill=INK, font=font(bold, 22 if zh else 19))
        x += box_width + 20

    filename = f"ai-subscription-payment-troubleshooting-social-{language}.png"
    image.save(IMAGES / filename, quality=96)


def make_dev_cover():
    image = Image.new("RGB", (1000, 420), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 24, 420), fill=GREEN)
    # DEV uses a wider article cover but crops social previews to roughly 803x420.
    # Keep all meaningful text inside the centered social-preview safe area.
    safe_left = 120
    draw.text((safe_left, 44), "CHONGGROK · BILLING STATE MACHINE", fill=GREEN, font=font(EN_BOLD, 19))
    draw.text((safe_left, 96), "Payment succeeded.", fill=INK, font=font(EN_BOLD, 44))
    draw.text((safe_left, 151), "Why is the account still Free?", fill=INK, font=font(EN_BOLD, 38))

    states = ["AUTHORIZED", "CAPTURED", "SUBSCRIPTION", "ENTITLEMENT"]
    widths = [150, 145, 170, 165]
    x = safe_left
    for index, state in enumerate(states):
        width = widths[index]
        draw.rounded_rectangle((x, 275, x + width, 344), radius=9, fill=WHITE, outline=LINE, width=2)
        label_face = font(EN_BOLD, 14)
        label_width = draw.textbbox((0, 0), state, font=label_face)[2]
        draw.text((x + (width - label_width) / 2, 299), state, fill=GREEN, font=label_face)
        x += width
        if index < len(states) - 1:
            draw.line((x + 6, 309, x + 22, 309), fill=AMBER, width=3)
            draw.polygon([(x + 22, 303), (x + 31, 309), (x + 22, 315)], fill=AMBER)
            x += 36
    draw.text((safe_left, 373), "A practical troubleshooting model for AI subscriptions", fill=MUTED, font=font(EN, 19))
    image.save(OUTREACH_ASSETS / "dev-ai-subscription-payment-state-machine-cover.png", quality=96)


def make_infographic(language):
    zh = language == "zh"
    image = Image.new("RGB", (1200, 1800), BG)
    draw = ImageDraw.Draw(image)
    regular = CN if zh else EN
    bold = CN_BOLD if zh else EN_BOLD

    draw.rectangle((0, 0, 1200, 18), fill=GREEN)
    draw.text((65, 50), "CHONGGROK · 2026", fill=GREEN, font=font(EN_BOLD, 23))
    title = "AI 订阅付款排障决策树" if zh else "AI Subscription Payment Troubleshooting"
    draw.text((65, 105), title, fill=INK, font=font(bold, 50 if zh else 45))
    subtitle = "ChatGPT · Grok · Claude · Gemini" if zh else "ChatGPT · Grok · Claude · Gemini"
    draw.text((65, 180), subtitle, fill=MUTED, font=font(regular, 25))

    warning = "先停止重复付款：预授权、最终扣款、有效订阅和账号权益是四个不同状态。" if zh else "Stop duplicate payment: authorization, capture, subscription and entitlement are separate states."
    draw.rounded_rectangle((65, 240, 1135, 355), radius=14, fill="#fff4ee", outline="#e6c8b6", width=2)
    draw_wrapped(draw, (100, 270), warning, font(bold, 28), RED, 995, 39)

    steps = [
        ("01  保存证据" if zh else "01  PRESERVE EVIDENCE", [
            "记录准确时间、金额、币种、订单号和错误" if zh else "Record time, amount, currency, order ID and error",
            "判断银行显示待处理、预授权还是最终入账" if zh else "Classify pending, authorized or completed bank state",
        ]),
        ("02  找到购买入口" if zh else "02  TRACE THE BILLING CHANNEL", [
            "官网、App Store、Google Play、X、Google One 或第三方" if zh else "Website, App Store, Google Play, X, Google One or third party",
            "由实际账单方处理取消、退款和交易状态" if zh else "The billing owner handles charges, cancellations and refunds",
        ]),
        ("03  核对原购买账号" if zh else "03  CONFIRM THE ORIGINAL ACCOUNT", [
            "商店账号、付款资料和产品账号可能不同" if zh else "Store, billing profile and product account can be different",
            "使用原购买时的登录方式，不按头像或昵称猜测" if zh else "Use the original sign-in method; do not infer from a display name",
        ]),
        ("04  检查订阅与权益" if zh else "04  CHECK SUBSCRIPTION AND ENTITLEMENT", [
            "原入口查有效订阅，再回官方产品页验收" if zh else "Check the original channel, then verify on the official product page",
            "已扣款仍为 Free 时进入对应产品专题" if zh else "Route charged-but-Free cases to the product-specific guide",
        ]),
        ("05  联系正确支持方" if zh else "05  CONTACT THE STATE OWNER", [
            "银行管预授权；商店管账单；产品方管权益" if zh else "Bank owns authorization; store owns billing; product owns entitlement",
            "ChongGrok 只处理 ChongGrok 的订单与履约记录" if zh else "ChongGrok handles only its own order and fulfillment record",
        ]),
    ]

    y = 390
    for heading, bullets in steps:
        draw.rounded_rectangle((65, y, 1135, y + 220), radius=14, fill=WHITE, outline=LINE, width=2)
        draw.ellipse((95, y + 28, 143, y + 76), fill=GREEN)
        draw.text((165, y + 30), heading, fill=GREEN, font=font(bold, 29 if zh else 25))
        by = y + 95
        for bullet in bullets:
            draw.ellipse((101, by + 10, 113, by + 22), fill=AMBER)
            draw_wrapped(draw, (135, by), bullet, font(regular, 25 if zh else 23), INK, 935, 34)
            by += 54
        if y < 1200:
            draw.polygon([(585, y + 228), (615, y + 228), (600, y + 248)], fill=GREEN)
        y += 245

    footer_box_y = 1618
    draw.rounded_rectangle((65, footer_box_y, 1135, 1732), radius=14, fill=PALE, outline="#9fc9bb", width=2)
    footer = "只有确认没有有效订阅、待处理扣款或退款后，才重新评估购买。" if zh else "Only reconsider purchase after active plans, pending charges and refunds are ruled out."
    draw_wrapped(draw, (100, footer_box_y + 30), footer, font(bold, 27), GREEN, 985, 38)
    url = "he20000405-pixel.github.io/resources/ai-subscription-payment-troubleshooting/" if zh else "he20000405-pixel.github.io/en/resources/ai-subscription-payment-troubleshooting/"
    draw.text((65, 1760), url, fill=MUTED, font=font(EN, 18))

    image.save(IMAGES / f"ai-subscription-payment-troubleshooting-{language}.png", quality=96)


def register_pdf_fonts(language):
    zh = language == "zh"
    regular = "PAY-CN" if zh else "PAY-EN"
    bold = "PAY-CN-BOLD" if zh else "PAY-EN-BOLD"
    pdfmetrics.registerFont(TTFont(regular, str(CN if zh else EN)))
    pdfmetrics.registerFont(TTFont(bold, str(CN_BOLD if zh else EN_BOLD)))
    return regular, bold


def draw_pdf_lines(doc, text, x, y, max_chars, face, size, leading, color=INK):
    doc.setFont(face, size)
    doc.setFillColor(HexColor(color))
    if any("\u4e00" <= c <= "\u9fff" for c in text):
        lines = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
    else:
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = (current + " " + word).strip()
            if len(candidate) <= max_chars:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    for line in lines:
        doc.drawString(x, y, line)
        y -= leading
    return y


def make_pdf(language):
    zh = language == "zh"
    regular, bold = register_pdf_fonts(language)
    path = DOWNLOADS / f"ai-subscription-payment-troubleshooting-{language}.pdf"
    doc = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    margin = 44

    def header(page):
        doc.setFillColor(HexColor(GREEN))
        doc.rect(0, height - 14, width, 14, stroke=0, fill=1)
        doc.setFont(bold, 9.5)
        doc.drawString(margin, height - 35, "CHONGGROK · AI PAYMENT TROUBLESHOOTING")
        doc.setFillColor(HexColor(MUTED))
        doc.setFont(regular, 8)
        doc.drawRightString(width - margin, 23, f"{page} / 2 · he20000405-pixel.github.io")

    header(1)
    title = "AI 订阅付款排障决策树" if zh else "AI Subscription Payment Troubleshooting"
    doc.setFillColor(HexColor(INK))
    doc.setFont(bold, 22 if zh else 20)
    doc.drawString(margin, height - 74, title)
    doc.setFillColor(HexColor(MUTED))
    doc.setFont(regular, 10)
    doc.drawString(margin, height - 95, "ChatGPT · Grok · Claude · Gemini")

    notice = "先停止重复付款。预授权、最终扣款、有效订阅和账号权益是不同状态。" if zh else "Stop duplicate payment. Authorization, capture, subscription and entitlement are separate states."
    doc.setFillColor(HexColor("#fff4ee"))
    doc.roundRect(margin, height - 150, width - margin * 2, 38, 6, stroke=0, fill=1)
    doc.setFillColor(HexColor(RED))
    doc.setFont(bold, 9.8)
    doc.drawString(margin + 12, height - 136, notice)

    sections = [
        ("01 保存证据" if zh else "01 PRESERVE EVIDENCE", [
            "记录时间、金额、币种、订单号和错误。" if zh else "Record time, amount, currency, order ID and error.",
            "判断银行状态是待处理、预授权还是最终入账。" if zh else "Classify the bank state as pending, authorized or completed.",
        ]),
        ("02 找到购买入口" if zh else "02 TRACE THE BILLING CHANNEL", [
            "官网、App Store、Google Play、X、Google One 或第三方。" if zh else "Website, App Store, Google Play, X, Google One or third party.",
            "实际账单方负责取消、退款和交易状态。" if zh else "The billing owner handles charges, cancellations and refunds.",
        ]),
        ("03 核对原购买账号" if zh else "03 CONFIRM THE ORIGINAL ACCOUNT", [
            "商店账号、付款资料和产品账号可能不同。" if zh else "Store, billing profile and product account may be different.",
            "使用购买时的登录方式，不按头像或昵称猜测。" if zh else "Use the original sign-in method; do not infer from a display name.",
        ]),
        ("04 检查订阅与权益" if zh else "04 CHECK SUBSCRIPTION AND ENTITLEMENT", [
            "原入口查有效订阅，再回官方产品页验收。" if zh else "Check the original channel, then the official product page.",
            "账单成功但仍为 Free 时进入对应产品专题。" if zh else "Route charged-but-Free cases to the product-specific guide.",
        ]),
        ("05 联系正确支持方" if zh else "05 CONTACT THE STATE OWNER", [
            "银行管预授权；商店管账单；产品方管权益。" if zh else "Bank owns authorization; store owns billing; product owns entitlement.",
            "ChongGrok 只处理自己的订单和履约记录。" if zh else "ChongGrok handles only its own order and fulfillment record.",
        ]),
    ]
    y = height - 175
    for heading, bullets in sections:
        box_h = 92
        doc.setFillColor(HexColor(PALE))
        doc.roundRect(margin, y - box_h, width - margin * 2, box_h - 6, 6, stroke=0, fill=1)
        doc.setFillColor(HexColor(GREEN))
        doc.setFont(bold, 11.5)
        doc.drawString(margin + 14, y - 23, heading)
        by = y - 45
        for bullet in bullets:
            doc.setFillColor(HexColor(AMBER))
            doc.circle(margin + 18, by + 3, 2, stroke=0, fill=1)
            doc.setFillColor(HexColor(INK))
            doc.setFont(regular, 9.2)
            doc.drawString(margin + 29, by, bullet)
            by -= 20
        y -= box_h
    doc.showPage()

    header(2)
    doc.setFillColor(HexColor(INK))
    doc.setFont(bold, 17)
    doc.drawString(margin, height - 70, "支持责任与证据" if zh else "Support ownership and evidence")

    owners = [
        ("银行" if zh else "Bank", "预授权、拒付、卡片限制" if zh else "Authorizations, declines and card restrictions"),
        ("Apple / Google Play", "应用商店扣款、取消和退款" if zh else "Store charges, cancellation and refunds"),
        ("X / Google One", "对应平台的账单和续费" if zh else "Billing and renewals on that platform"),
        ("AI 产品支持" if zh else "AI provider", "账单完成但账号权益缺失" if zh else "Completed billing with missing entitlement"),
        ("ChongGrok", "ChongGrok 订单、卡密或履约记录" if zh else "ChongGrok orders and fulfillment records"),
    ]
    y = height - 103
    for owner, detail in owners:
        doc.setFillColor(HexColor(WHITE))
        doc.setStrokeColor(HexColor(LINE))
        doc.roundRect(margin, y - 45, width - margin * 2, 40, 5, stroke=1, fill=1)
        doc.setFillColor(HexColor(GREEN))
        doc.setFont(bold, 9.8)
        doc.drawString(margin + 12, y - 28, owner)
        doc.setFillColor(HexColor(INK))
        doc.setFont(regular, 9)
        doc.drawString(margin + 125, y - 28, detail)
        y -= 48

    doc.setFillColor(HexColor(INK))
    doc.setFont(bold, 13)
    doc.drawString(margin, y - 12, "脱敏证据清单" if zh else "Redacted evidence checklist")
    evidence = [
        "产品、套餐、周期和购买入口" if zh else "Product, plan, term and billing channel",
        "时间、金额、币种、订单号和收据" if zh else "Time, amount, currency, order ID and receipt",
        "银行状态与原购买账号的脱敏标识" if zh else "Bank state and masked purchasing account identifier",
        "官方计划页面、错误、设备和已尝试步骤" if zh else "Official plan screen, error, device and attempted steps",
    ]
    ey = y - 38
    for item in evidence:
        doc.setFillColor(HexColor(AMBER))
        doc.circle(margin + 5, ey + 3, 2, stroke=0, fill=1)
        doc.setFillColor(HexColor(INK))
        doc.setFont(regular, 9.5)
        doc.drawString(margin + 16, ey, item)
        ey -= 22

    disclosure_y = 100
    doc.setFillColor(HexColor(PALE))
    doc.roundRect(margin, disclosure_y, width - margin * 2, 112, 7, stroke=0, fill=1)
    doc.setFillColor(HexColor(GREEN))
    doc.setFont(bold, 11)
    doc.drawString(margin + 14, disclosure_y + 84, "独立性与风险说明" if zh else "Independence and risk disclosure")
    disclosure = (
        "ChongGrok 是独立第三方，与相关 AI 公司和账单平台不存在隶属或官方合作。"
        if zh
        else "ChongGrok is independent and not officially partnered with the AI or billing providers."
    )
    draw_pdf_lines(doc, disclosure, margin + 14, disclosure_y + 61, 58 if zh else 76, regular, 8.7, 14)
    url = (
        "he20000405-pixel.github.io/resources/ai-subscription-payment-troubleshooting/"
        if zh
        else "he20000405-pixel.github.io/en/resources/ai-subscription-payment-troubleshooting/"
    )
    doc.setFont(regular, 7.8)
    doc.setFillColor(HexColor(MUTED))
    doc.drawString(margin + 14, disclosure_y + 19, url)
    doc.save()


if __name__ == "__main__":
    for lang in ("zh", "en"):
        make_social(lang)
        make_infographic(lang)
        make_pdf(lang)
    make_dev_cover()
