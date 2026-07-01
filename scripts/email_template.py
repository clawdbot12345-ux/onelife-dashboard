#!/usr/bin/env python3
"""
Onelife — master email template (2026 design system).

Single source of truth for the campaign email shell so every send — Tuesday
digest, Friday product, Monday article, monthly digest, ad-hoc — looks
identical: 620px card on #f4f1ea, #1b4332 logo header + accent bar, optional
hero, Georgia serif h1, Precious voice greeting, tinted product cards,
delivery banner, WhatsApp consult line, espresso footer with unsubscribe.

Import from the other scripts/*.py pipelines; do not paste inline HTML into
campaign scripts anymore (that is how the three renderers drifted apart —
different accent bars, footers and WhatsApp lines by June 2026).
"""

LOGO_URL = ("https://onelife.co.za/cdn/shop/files/"
            "OneLife_LOGO_51277c55-2099-4f3a-a659-ef42cdcac5d9.png?v=1671450106")
GREEN_DARK = "#1b4332"     # header, buttons, h1
GREEN_MID = "#2d6a4f"      # default accent bar + eyebrow
AMBER = "#b45309"          # product-spotlight accent
FOOTER_BG = "#14291e"
BODY_BG = "#f4f1ea"
WHATSAPP_NUMBER = "27713744910"
CARD_TINTS = [("#d8f3ea", "#0f766e"), ("#fdeac1", "#92400e"), ("#e7eaff", "#4338ca")]

# Klaviyo template-language fragments (plain strings — never f-string these)
GREETING = "Hi {{ first_name|default:'there' }} — Precious here."
UNSUBSCRIBE = "{% unsubscribe 'Unsubscribe' %}"

DELIVERY_LINE = ("\U0001F69A Free delivery over R400 nationwide · "
                 "\U0001F3EA Collect free at Centurion, Glen Village or Edenvale")
FOOTER_TAGLINE = "A real apothecary. Family-owned since 1996."
FOOTER_STORES = "Centurion · Glen Village · Edenvale · Free delivery over R400 nationwide"
TEXT_FOOTER = ("— Precious, One Life Health Consultant\n"
               "Onelife Health · Centurion · Glen Village · Edenvale\n"
               "Free delivery over R400 nationwide | Collect free in store\n"
               "onelife.co.za")


def utm(url, campaign_slug, content):
    sep = "&" if "?" in url else "?"
    return (f"{url}{sep}utm_source=klaviyo&utm_medium=email"
            f"&utm_campaign={campaign_slug}&utm_content={content}")


def whatsapp_link(prefill):
    from urllib.parse import quote
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(prefill)}"


def product_cards(products, campaign_slug):
    """Tinted product-card rows. Each product: name, url, and optionally
    price, blurb, badge. Returns table rows for a 100%-width table."""
    rows = ""
    for i, p in enumerate(products or []):
        prod_url = utm(p.get("url", "#"), campaign_slug, f"product-{i + 1}")
        bg, accent = CARD_TINTS[i % len(CARD_TINTS)]
        badge = p.get("badge", "")
        badge_html = (f'<p style="margin:0 0 4px;font-size:10px;letter-spacing:1.5px;'
                      f'text-transform:uppercase;color:{accent};font-weight:bold;">{badge}</p>'
                      if badge else "")
        price = p.get("price", "")
        price_html = (f' <span style="color:{accent};font-weight:800;">· {price}</span>'
                      if price else "")
        rows += f'''
<tr><td style="padding:16px 16px 14px;background:{bg};border-radius:12px;">
{badge_html}<p style="margin:0 0 6px;font-size:16px;font-weight:bold;color:#1a1a1a;"><a href="{prod_url}" style="color:#1a1a1a;text-decoration:none;">{p.get("name", "")}</a>{price_html}</p>
<p style="margin:0;font-size:13px;line-height:1.5;color:#374151;">{p.get("blurb", "")} <a href="{prod_url}" style="color:{accent};font-weight:bold;">Shop →</a></p>
</td></tr>
<tr><td style="height:10px;font-size:0;">&nbsp;</td></tr>'''
    return rows


def render_email(*, title, eyebrow, campaign_slug, intro_html,
                 accent=GREEN_MID, hero=None, cta=None, price=None,
                 extra_html=None, products=None, note_html=None,
                 whatsapp_lead="Not sure if it's right for you?",
                 whatsapp_prefill="Hi Precious, quick question about this week's email"):
    """Render the full campaign HTML document.

    hero:  {"src", "href", "alt"} or None
    cta:   {"label", "href"} or None (href should already be UTM-tagged)
    price: display price string shown large under the intro (product emails)
    extra_html: arbitrary block inserted after the CTA (article lists etc.)
    products: list for product_cards()
    note_html: inner HTML for the tinted note box (protocol CTA etc.)
    """
    hero_html = ""
    if hero:
        hero_html = (f'<tr><td><a href="{hero["href"]}"><img alt="{hero.get("alt", title)}" '
                     f'src="{hero["src"]}" style="display:block;width:100%;height:auto;" '
                     f'width="620"/></a></td></tr>')

    price_html = (f'<p style="margin:0 0 18px;font-size:24px;font-weight:800;'
                  f'color:{GREEN_DARK};">{price}</p>' if price else "")

    cta_html = ""
    if cta:
        cta_html = f'''<table cellpadding="0" cellspacing="0" role="presentation" width="100%"><tr><td align="center" style="padding:0 0 22px;">
<a href="{cta["href"]}" style="display:inline-block;background:{GREEN_DARK};color:#ffffff;padding:14px 30px;border-radius:10px;font-size:15px;font-weight:bold;text-decoration:none;">{cta["label"]}</a>
</td></tr></table>'''

    products_html = ""
    cards = product_cards(products, campaign_slug)
    if cards:
        products_html = (f'<table cellpadding="0" cellspacing="0" role="presentation" '
                         f'style="margin:0 0 14px;" width="100%">{cards}</table>')

    note_block = ""
    if note_html:
        note_block = f'''<table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 24px;" width="100%">
<tr><td style="padding:16px 20px;background:#f1f5f1;border-radius:12px;">
<p style="margin:0;font-size:13.5px;line-height:1.7;color:#374151;">{note_html}</p></td></tr></table>'''

    wa_url = whatsapp_link(whatsapp_prefill)

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1" name="viewport"/><title>{title}</title></head>
<body style="margin:0;padding:0;background:{BODY_BG};font-family:Arial,Helvetica,sans-serif;color:#374151;">
<table cellpadding="0" cellspacing="0" role="presentation" style="background:{BODY_BG};padding:28px 0;" width="100%"><tr><td align="center">
<table cellpadding="0" cellspacing="0" role="presentation" style="max-width:620px;background:#ffffff;border-radius:12px;overflow:hidden;" width="620">
<tr><td style="background:{GREEN_DARK};padding:22px 40px;text-align:center;">
<img alt="One Life Health" src="{LOGO_URL}" style="display:block;margin:0 auto;max-width:130px;height:auto;" width="130"/></td></tr>
<tr><td style="height:4px;background:{accent};font-size:0;line-height:0;">&nbsp;</td></tr>
{hero_html}
<tr><td style="padding:36px 40px 8px;">
<p style="margin:0 0 14px;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:{accent};font-weight:bold;">{eyebrow}</p>
<h1 style="margin:0 0 16px;font-family:Georgia,'Times New Roman',serif;font-size:28px;line-height:1.2;color:{GREEN_DARK};font-weight:normal;">{title}</h1>
<p style="margin:0 0 18px;font-size:15px;line-height:1.65;">{GREETING} {intro_html}</p>
{price_html}{cta_html}{extra_html or ""}{products_html}
<table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 24px;" width="100%">
<tr><td style="padding:16px 20px;background:#f1f5f1;border-radius:12px;text-align:center;">
<p style="margin:0;font-size:13.5px;line-height:1.7;color:#374151;">{DELIVERY_LINE}</p></td></tr></table>
{note_block}
<p style="margin:0 0 6px;font-size:13.5px;line-height:1.6;color:#555;">{whatsapp_lead} <a href="{wa_url}" style="color:{GREEN_DARK};font-weight:bold;">WhatsApp me</a> — free, no pressure.</p>
<p style="margin:20px 0 4px;font-size:14px;">— Precious</p>
<p style="margin:0 0 28px;font-size:12px;color:#888;">One Life Health Consultant · Centurion</p></td></tr>
<tr><td style="background:{FOOTER_BG};padding:20px 40px;text-align:center;">
<p style="margin:0 0 4px;font-family:Georgia,serif;font-size:16px;color:#ffffff;">{FOOTER_TAGLINE}</p>
<p style="margin:0;font-size:11px;color:#9db8a8;">{FOOTER_STORES}</p>
<p style="margin:12px 0 0;font-size:11px;color:#9db8a8;">{UNSUBSCRIBE} · <a href="https://onelife.co.za" style="color:#9db8a8;">onelife.co.za</a></p></td></tr>
</table></td></tr></table></body></html>'''
