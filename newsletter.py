"""
Fiona Newsletter — weekly cybersecurity digest for C&S Wholesale Groceries.

Generates a professional HTML email and sends it via SMTP.
Configure via environment variables:
    SMTP_HOST       SMTP server hostname        (default: smtp.office365.com)
    SMTP_PORT       SMTP port                   (default: 587)
    SMTP_USER       SMTP login / From address   (required to send)
    SMTP_PASSWORD   SMTP password               (required to send)
    SMTP_FROM_NAME  Display name                (default: Fiona · C&S Cybersecurity)
    NEWSLETTER_BASE_URL  Base URL for unsubscribe links (default: http://localhost:8000)
"""

import os
import smtplib
import textwrap
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Optional

from security_tips import get_tip_of_the_day
import database as db

# ── Config ────────────────────────────────────────────────────────────────────
SMTP_HOST      = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER      = os.getenv("SMTP_USER", "")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Fiona · C&S Cybersecurity")
BASE_URL       = os.getenv("NEWSLETTER_BASE_URL", "http://localhost:8000")

CYBERSEC_EMAIL  = os.getenv("CYBERSEC_EMAIL", "CyberSecurity@cswg.com")
CYBERSEC_PHONE  = "603-354-7500"
CYBERSEC_SITE   = "https://sites.google.com/cswg.com/cybersecurity"

# Brand colours (mirror the app's CSS variables)
COLOR_BG        = "#0f1117"
COLOR_HEADER_BG = "#141820"
COLOR_CARD      = "#1a1e27"
COLOR_ACCENT    = "#34d399"   # green
COLOR_ACCENT2   = "#60a5fa"   # blue
COLOR_ACCENT3   = "#f472b6"   # pink
COLOR_TEXT      = "#e4e6ea"
COLOR_MUTED     = "#9da3ae"
COLOR_BORDER    = "#2c313a"
COLOR_DANGER    = "#f87171"
COLOR_ORANGE    = "#fb923c"


# ── Data collection ───────────────────────────────────────────────────────────

def collect_newsletter_data(department: Optional[str] = None) -> Dict:
    """Pull together everything the template needs for one newsletter edition."""
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    tip       = get_tip_of_the_day(department)
    summary   = db.get_analytics_summary(days=7)
    popular   = db.get_popular_questions(department=department, limit=5)
    gaps      = db.get_kb_gaps(limit=5)
    feedback  = db.get_feedback_stats(days=7)
    subs      = db.get_active_subscribers()

    # Derive a second tip for the "Quick Security Reminder" section
    tomorrow_tip = get_tip_of_the_day.__wrapped__(department) if hasattr(
        get_tip_of_the_day, "__wrapped__") else _pick_tip(department, offset=1)

    return {
        "edition_date":    date.today().strftime("%B %d, %Y"),
        "week_label":      f"Week of {(date.today() - timedelta(days=6)).strftime('%b %d')} – {date.today().strftime('%b %d, %Y')}",
        "department":      department,
        "tip":             tip,
        "reminder_tip":    _pick_tip(department, offset=3),
        "total_queries":   summary.get("total_queries", 0),
        "by_department":   summary.get("by_department", [])[:5],
        "popular":         popular,
        "gaps":            gaps,
        "feedback":        feedback,
        "subscriber_count": len(subs),
    }


def _pick_tip(department: Optional[str], offset: int = 0) -> Dict:
    """Pick a tip at a fixed offset from today's index."""
    from security_tips import TIPS
    today_ord = date.today().toordinal() + offset
    if department:
        pool = [t for t in TIPS if t["departments"] is None or department in t["departments"]]
    else:
        pool = TIPS
    if not pool:
        pool = TIPS
    return pool[today_ord % len(pool)]


# ── HTML template ─────────────────────────────────────────────────────────────

def generate_html(data: Dict) -> str:
    """Return a complete, inlined HTML email string."""

    dept_line  = f" &mdash; {data['department']}" if data.get("department") else ""
    tip_text   = data["tip"].get("tip", "")
    reminder   = data["reminder_tip"].get("tip", "")
    queries    = data["total_queries"]
    popular    = data["popular"]
    gaps       = data["gaps"]
    fb         = data["feedback"]
    sat        = fb.get("satisfaction_pct", 0)
    thumbs_up  = fb.get("up", 0)
    thumbs_dn  = fb.get("down", 0)

    # Build popular questions rows
    popular_rows = ""
    if popular:
        for i, q in enumerate(popular[:5], 1):
            query_text = (q.get("query") or "")[:90]
            cnt        = q.get("cnt", 1)
            popular_rows += f"""
            <tr>
              <td style="padding:10px 14px;border-bottom:1px solid {COLOR_BORDER};
                         color:{COLOR_TEXT};font-size:14px;line-height:1.5;">
                <span style="color:{COLOR_ACCENT};font-weight:600;margin-right:8px;">{i}.</span>
                {query_text}
              </td>
              <td style="padding:10px 14px;border-bottom:1px solid {COLOR_BORDER};
                         color:{COLOR_MUTED};font-size:13px;text-align:right;white-space:nowrap;">
                {cnt}x
              </td>
            </tr>"""
    else:
        popular_rows = f"""
        <tr>
          <td colspan="2" style="padding:16px;color:{COLOR_MUTED};font-size:14px;text-align:center;">
            No queries recorded this week yet.
          </td>
        </tr>"""

    # Build gaps rows
    gap_rows = ""
    if gaps:
        for g in gaps[:4]:
            q = (g.get("query") or "")[:80]
            reason = "Low confidence" if g.get("reason") == "low_confidence" else "Negative feedback"
            badge_color = COLOR_ORANGE if g.get("reason") == "low_confidence" else COLOR_DANGER
            gap_rows += f"""
            <tr>
              <td style="padding:10px 14px;border-bottom:1px solid {COLOR_BORDER};
                         color:{COLOR_TEXT};font-size:13px;">{q}</td>
              <td style="padding:10px 14px;border-bottom:1px solid {COLOR_BORDER};text-align:right;">
                <span style="background:{badge_color}22;color:{badge_color};
                             border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;">
                  {reason}
                </span>
              </td>
            </tr>"""
    else:
        gap_rows = f"""
        <tr>
          <td colspan="2" style="padding:16px;color:{COLOR_MUTED};font-size:14px;text-align:center;">
            No knowledge gaps detected this week. 🎉
          </td>
        </tr>"""

    # By-department stats pills
    dept_pills = ""
    dept_colors = [COLOR_ACCENT, COLOR_ACCENT2, COLOR_ACCENT3, COLOR_ORANGE, "#a78bfa"]
    for i, row in enumerate(data["by_department"][:5]):
        c = dept_colors[i % len(dept_colors)]
        dept_pills += f"""
          <span style="display:inline-block;margin:4px;background:{c}22;color:{c};
                       border:1px solid {c}44;border-radius:20px;
                       padding:4px 14px;font-size:13px;font-weight:500;">
            {row.get('department','?')} &nbsp; <strong>{row.get('cnt',0)}</strong>
          </span>"""
    if not dept_pills:
        dept_pills = f'<span style="color:{COLOR_MUTED};font-size:13px;">No data yet</span>'

    # Satisfaction bar
    sat_width   = max(4, int(sat))
    sat_color   = COLOR_ACCENT if sat >= 70 else (COLOR_ORANGE if sat >= 40 else COLOR_DANGER)
    sat_label   = f"{sat:.0f}%"

    unsubscribe_placeholder = f"{BASE_URL}/unsubscribe?email={{{{email}}}}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <title>Fiona Weekly · C&amp;S Cybersecurity{dept_line}</title>
  <!--[if mso]><noscript><xml><o:OfficeDocumentSettings>
  <o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
</head>
<body style="margin:0;padding:0;background:{COLOR_BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif;">

<!-- Preheader (hidden preview text) -->
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">
  Your weekly cybersecurity digest from Fiona &amp; the C&amp;S Cybersecurity Team &bull; {data['edition_date']}
  &nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;
</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:{COLOR_BG};min-height:100vh;">
<tr><td align="center" style="padding:32px 16px;">

  <!-- Outer wrapper -->
  <table role="presentation" width="620" cellpadding="0" cellspacing="0" border="0"
         style="max-width:620px;width:100%;">

    <!-- ══ HEADER ══════════════════════════════════════════════════════════ -->
    <tr>
      <td style="background:{COLOR_HEADER_BG};border-radius:12px 12px 0 0;
                 border:1px solid {COLOR_BORDER};border-bottom:none;
                 padding:32px 40px 28px;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td>
              <!-- Avatar + Wordmark -->
              <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="vertical-align:middle;">
                    <div style="width:48px;height:48px;border-radius:50%;
                                background:{COLOR_ACCENT};display:inline-block;
                                text-align:center;line-height:48px;
                                font-size:22px;font-weight:700;color:{COLOR_BG};">F</div>
                  </td>
                  <td style="vertical-align:middle;padding-left:14px;">
                    <div style="font-size:22px;font-weight:700;color:{COLOR_TEXT};letter-spacing:-0.3px;">
                      Fiona <span style="color:{COLOR_MUTED};font-weight:400;">by</span>
                      <span style="color:{COLOR_ACCENT};"> C&amp;S</span>
                    </div>
                    <div style="font-size:12px;color:{COLOR_MUTED};margin-top:2px;letter-spacing:0.5px;">
                      CYBERSECURITY WEEKLY{dept_line.replace(' &mdash; ', ' · ').upper()}
                    </div>
                  </td>
                </tr>
              </table>
            </td>
            <td align="right" style="vertical-align:middle;">
              <div style="font-size:12px;color:{COLOR_MUTED};">{data['edition_date']}</div>
              <div style="margin-top:6px;">
                <span style="background:{COLOR_ACCENT}22;color:{COLOR_ACCENT};
                             border:1px solid {COLOR_ACCENT}44;border-radius:20px;
                             padding:3px 12px;font-size:11px;font-weight:600;letter-spacing:0.5px;">
                  WEEKLY DIGEST
                </span>
              </div>
            </td>
          </tr>
        </table>

        <!-- Divider -->
        <div style="height:1px;background:linear-gradient(to right,{COLOR_ACCENT}88,{COLOR_BORDER});
                    margin-top:24px;"></div>

        <!-- Subtitle line -->
        <div style="margin-top:16px;font-size:14px;color:{COLOR_MUTED};line-height:1.5;">
          Your weekly briefing on what matters in cybersecurity at C&amp;S Wholesale Groceries.
          Powered by Fiona, your AI-driven security assistant.
        </div>
      </td>
    </tr>

    <!-- ══ BODY ════════════════════════════════════════════════════════════ -->
    <tr>
      <td style="background:{COLOR_CARD};border:1px solid {COLOR_BORDER};
                 border-top:none;border-bottom:none;padding:0 40px;">

        <!-- ── 1. SECURITY TIP OF THE WEEK ───────────────────────────── -->
        <div style="padding:32px 0 0;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:{COLOR_ACCENT};margin-bottom:12px;">
            🔒&nbsp; SECURITY TIP OF THE WEEK
          </div>
          <div style="background:{COLOR_ACCENT}11;border-left:4px solid {COLOR_ACCENT};
                      border-radius:0 8px 8px 0;padding:18px 20px;">
            <div style="font-size:15px;color:{COLOR_TEXT};line-height:1.7;">
              {_md_to_html(tip_text)}
            </div>
          </div>
        </div>

        <!-- ── 2. THIS WEEK IN NUMBERS ────────────────────────────────── -->
        <div style="padding:28px 0 0;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:{COLOR_ACCENT2};margin-bottom:16px;">
            📊&nbsp; THIS WEEK IN NUMBERS
          </div>

          <!-- Stats row -->
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <!-- Queries card -->
              <td width="33%" style="padding-right:8px;">
                <div style="background:{COLOR_BG};border:1px solid {COLOR_BORDER};
                            border-radius:10px;padding:16px;text-align:center;">
                  <div style="font-size:32px;font-weight:700;color:{COLOR_ACCENT2};">{queries}</div>
                  <div style="font-size:11px;color:{COLOR_MUTED};margin-top:4px;
                              text-transform:uppercase;letter-spacing:0.5px;">Queries</div>
                </div>
              </td>
              <!-- Thumbs up -->
              <td width="33%" style="padding:0 4px;">
                <div style="background:{COLOR_BG};border:1px solid {COLOR_BORDER};
                            border-radius:10px;padding:16px;text-align:center;">
                  <div style="font-size:32px;font-weight:700;color:{COLOR_ACCENT};">{thumbs_up}</div>
                  <div style="font-size:11px;color:{COLOR_MUTED};margin-top:4px;
                              text-transform:uppercase;letter-spacing:0.5px;">Helpful ✓</div>
                </div>
              </td>
              <!-- Satisfaction -->
              <td width="33%" style="padding-left:8px;">
                <div style="background:{COLOR_BG};border:1px solid {COLOR_BORDER};
                            border-radius:10px;padding:16px;text-align:center;">
                  <div style="font-size:32px;font-weight:700;color:{sat_color};">{sat_label}</div>
                  <div style="font-size:11px;color:{COLOR_MUTED};margin-top:4px;
                              text-transform:uppercase;letter-spacing:0.5px;">Satisfaction</div>
                </div>
              </td>
            </tr>
          </table>

          <!-- Satisfaction bar -->
          <div style="margin-top:14px;">
            <div style="font-size:12px;color:{COLOR_MUTED};margin-bottom:6px;">
              User satisfaction this week
            </div>
            <div style="background:{COLOR_BG};border-radius:4px;height:8px;overflow:hidden;
                        border:1px solid {COLOR_BORDER};">
              <div style="background:{sat_color};width:{sat_width}%;height:100%;
                          border-radius:4px;transition:width .3s;"></div>
            </div>
            <div style="font-size:11px;color:{COLOR_MUTED};margin-top:4px;">
              {thumbs_up} helpful &nbsp;·&nbsp; {thumbs_dn} not helpful
            </div>
          </div>

          <!-- Department activity pills -->
          <div style="margin-top:16px;">
            <div style="font-size:12px;color:{COLOR_MUTED};margin-bottom:8px;">
              Most active departments
            </div>
            <div>{dept_pills}</div>
          </div>
        </div>

        <!-- ── 3. TOP QUESTIONS THIS WEEK ─────────────────────────────── -->
        <div style="padding:28px 0 0;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:{COLOR_ACCENT3};margin-bottom:12px;">
            ❓&nbsp; TOP QUESTIONS THIS WEEK
          </div>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background:{COLOR_BG};border:1px solid {COLOR_BORDER};border-radius:10px;
                        overflow:hidden;">
            {popular_rows}
          </table>
        </div>

        <!-- ── 4. KNOWLEDGE GAPS ──────────────────────────────────────── -->
        <div style="padding:28px 0 0;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:{COLOR_ORANGE};margin-bottom:8px;">
            🔍&nbsp; KNOWLEDGE GAPS TO ADDRESS
          </div>
          <div style="font-size:13px;color:{COLOR_MUTED};margin-bottom:12px;">
            Questions where Fiona had low confidence or received negative feedback.
            Consider adding documentation in these areas.
          </div>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                 style="background:{COLOR_BG};border:1px solid {COLOR_BORDER};border-radius:10px;
                        overflow:hidden;">
            {gap_rows}
          </table>
        </div>

        <!-- ── 5. QUICK SECURITY REMINDER ────────────────────────────── -->
        <div style="padding:28px 0 0;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:#a78bfa;margin-bottom:12px;">
            💡&nbsp; QUICK SECURITY REMINDER
          </div>
          <div style="background:#a78bfa11;border-left:4px solid #a78bfa;
                      border-radius:0 8px 8px 0;padding:16px 20px;">
            <div style="font-size:14px;color:{COLOR_TEXT};line-height:1.7;">
              {_md_to_html(reminder)}
            </div>
          </div>
        </div>

        <!-- ── 6. QUICK ACTIONS ───────────────────────────────────────── -->
        <div style="padding:28px 0 32px;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;
                      color:{COLOR_MUTED};margin-bottom:16px;">
            ⚡&nbsp; QUICK ACTIONS
          </div>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td width="50%" style="padding-right:6px;">
                <a href="{CYBERSEC_SITE}" target="_blank" rel="noopener"
                   style="display:block;background:{COLOR_ACCENT}22;
                          border:1px solid {COLOR_ACCENT}44;border-radius:8px;
                          padding:14px 16px;text-decoration:none;text-align:center;">
                  <div style="font-size:20px;">🌐</div>
                  <div style="font-size:13px;font-weight:600;color:{COLOR_ACCENT};margin-top:6px;">
                    Cybersecurity Website
                  </div>
                  <div style="font-size:11px;color:{COLOR_MUTED};margin-top:3px;">
                    Policies, training &amp; resources
                  </div>
                </a>
              </td>
              <td width="50%" style="padding-left:6px;">
                <a href="mailto:{CYBERSEC_EMAIL}" target="_blank"
                   style="display:block;background:{COLOR_ACCENT2}22;
                          border:1px solid {COLOR_ACCENT2}44;border-radius:8px;
                          padding:14px 16px;text-decoration:none;text-align:center;">
                  <div style="font-size:20px;">📧</div>
                  <div style="font-size:13px;font-weight:600;color:{COLOR_ACCENT2};margin-top:6px;">
                    Contact the Team
                  </div>
                  <div style="font-size:11px;color:{COLOR_MUTED};margin-top:3px;">
                    {CYBERSEC_EMAIL}
                  </div>
                </a>
              </td>
            </tr>
          </table>

          <!-- Phone CTA -->
          <div style="margin-top:12px;text-align:center;padding:12px;
                      background:{COLOR_BG};border:1px solid {COLOR_BORDER};border-radius:8px;">
            <span style="font-size:13px;color:{COLOR_MUTED};">
              🚨&nbsp; <strong style="color:{COLOR_TEXT};">Urgent incident?</strong>
              Call the Cybersecurity Helpdesk:
              <a href="tel:{CYBERSEC_PHONE}" style="color:{COLOR_ACCENT3};text-decoration:none;
                                                    font-weight:600;">{CYBERSEC_PHONE}</a>
            </span>
          </div>
        </div>

      </td>
    </tr><!-- end body row -->

    <!-- ══ FOOTER ══════════════════════════════════════════════════════════ -->
    <tr>
      <td style="background:{COLOR_HEADER_BG};border:1px solid {COLOR_BORDER};
                 border-top:none;border-radius:0 0 12px 12px;padding:24px 40px;">

        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="text-align:center;">
              <div style="font-size:13px;font-weight:600;color:{COLOR_TEXT};margin-bottom:6px;">
                Fiona &mdash; C&amp;S Wholesale Groceries Cybersecurity Assistant
              </div>
              <div style="font-size:12px;color:{COLOR_MUTED};line-height:1.8;">
                {CYBERSEC_EMAIL} &nbsp;·&nbsp; {CYBERSEC_PHONE}<br/>
                <a href="{CYBERSEC_SITE}" style="color:{COLOR_ACCENT};text-decoration:none;">
                  Cybersecurity Website
                </a>
              </div>

              <!-- Divider -->
              <div style="height:1px;background:{COLOR_BORDER};margin:16px auto;width:80%;"></div>

              <div style="font-size:11px;color:{COLOR_MUTED};line-height:1.7;">
                You received this email because you subscribed to the Fiona Weekly Digest.<br/>
                <a href="{unsubscribe_placeholder}"
                   style="color:{COLOR_MUTED};text-decoration:underline;">
                  Unsubscribe
                </a>
                &nbsp;·&nbsp;
                <a href="{CYBERSEC_SITE}"
                   style="color:{COLOR_MUTED};text-decoration:underline;">
                  Privacy Policy
                </a>
              </div>

              <div style="margin-top:14px;font-size:11px;color:{COLOR_BORDER};">
                © {date.today().year} C&amp;S Wholesale Grocers, LLC. All rights reserved.
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>

  </table><!-- end outer wrapper -->
</td></tr>
</table><!-- end full-width -->
</body>
</html>"""
    return html


def generate_plain_text(data: Dict) -> str:
    """Plain-text fallback for email clients that don't render HTML."""
    tip     = data["tip"].get("tip", "")
    reminder= data["reminder_tip"].get("tip", "")
    popular = data["popular"]
    fb      = data["feedback"]

    lines = [
        f"FIONA WEEKLY · C&S CYBERSECURITY DIGEST",
        f"{data['edition_date']}",
        "=" * 60,
        "",
        "🔒 SECURITY TIP OF THE WEEK",
        "-" * 40,
        _strip_md(tip),
        "",
        "📊 THIS WEEK IN NUMBERS",
        "-" * 40,
        f"  Queries:      {data['total_queries']}",
        f"  Helpful:      {fb.get('up', 0)}",
        f"  Satisfaction: {fb.get('satisfaction_pct', 0):.0f}%",
        "",
    ]

    if popular:
        lines += ["❓ TOP QUESTIONS THIS WEEK", "-" * 40]
        for i, q in enumerate(popular[:5], 1):
            lines.append(f"  {i}. {(q.get('query') or '')[:80]}")
        lines.append("")

    lines += [
        "💡 QUICK SECURITY REMINDER",
        "-" * 40,
        _strip_md(reminder),
        "",
        "⚡ QUICK ACTIONS",
        "-" * 40,
        f"  Cybersecurity Website: {CYBERSEC_SITE}",
        f"  Contact Team:          {CYBERSEC_EMAIL}",
        f"  Helpdesk:              {CYBERSEC_PHONE}",
        "",
        "=" * 60,
        "You received this because you subscribed to the Fiona Weekly Digest.",
        f"© {date.today().year} C&S Wholesale Grocers, LLC.",
    ]
    return "\n".join(lines)


# ── Markdown helpers ──────────────────────────────────────────────────────────

def _md_to_html(text: str) -> str:
    """Convert the minimal markdown used in tips (**bold**, `code`) to HTML."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e4e6ea;">\1</strong>', text)
    text = re.sub(r'`(.+?)`',        r'<code style="background:#2c313a;padding:1px 5px;'
                                      r'border-radius:3px;font-family:monospace;">\1</code>', text)
    return text


def _strip_md(text: str) -> str:
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`(.+?)`',        r'\1', text)
    return text


# ── SMTP sender ───────────────────────────────────────────────────────────────

class NewsletterSender:
    def __init__(self):
        self.host      = SMTP_HOST
        self.port      = SMTP_PORT
        self.user      = SMTP_USER
        self.password  = SMTP_PASSWORD
        self.from_name = SMTP_FROM_NAME

    def is_configured(self) -> bool:
        return bool(self.user and self.password)

    def send(self, to_addresses: List[str], subject: str, html: str, plain: str) -> Dict:
        """Send the newsletter to a list of addresses. Returns a result dict."""
        if not to_addresses:
            return {"sent": 0, "failed": 0, "error": "No recipients"}

        if not self.is_configured():
            return {
                "sent": 0,
                "failed": len(to_addresses),
                "error": "SMTP not configured. Set SMTP_USER and SMTP_PASSWORD in .env",
            }

        sent = 0
        failed = []

        try:
            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.user, self.password)

                for addr in to_addresses:
                    try:
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = subject
                        msg["From"]    = f"{self.from_name} <{self.user}>"
                        msg["To"]      = addr

                        # Plain text goes first; HTML is preferred by clients
                        msg.attach(MIMEText(plain, "plain", "utf-8"))
                        # Personalise unsubscribe link
                        personalised_html = html.replace("{{email}}", addr)
                        msg.attach(MIMEText(personalised_html, "html", "utf-8"))

                        server.sendmail(self.user, addr, msg.as_string())
                        sent += 1
                        print(f"  ✉  Sent newsletter to {addr}")
                    except Exception as e:
                        failed.append(addr)
                        print(f"  ✗  Failed to send to {addr}: {e}")

        except Exception as e:
            return {"sent": sent, "failed": len(to_addresses), "error": str(e)}

        return {"sent": sent, "failed": len(failed), "failed_addresses": failed}


def send_weekly_newsletter(department: Optional[str] = None,
                           extra_recipients: Optional[List[str]] = None) -> Dict:
    """
    Build and send the weekly newsletter to all active subscribers.
    extra_recipients are added on top of DB subscribers (useful for test sends).
    """
    data  = collect_newsletter_data(department)
    html  = generate_html(data)
    plain = generate_plain_text(data)

    week  = data["week_label"]
    dept  = f" ({department})" if department else ""
    subject = f"Fiona Weekly Digest{dept} · {week}"

    subs = [s["email"] for s in db.get_active_subscribers()]
    if extra_recipients:
        for e in extra_recipients:
            if e not in subs:
                subs.append(e)

    sender = NewsletterSender()
    result = sender.send(subs, subject, html, plain)
    result["subject"] = subject
    result["recipients"] = subs
    return result
