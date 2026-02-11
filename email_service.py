"""
Email service for Fiona — builds mailto: links that open the user's email client
with a pre-filled incident report or escalation addressed to CyberSecurity@cswg.com.
"""
import urllib.parse
from datetime import datetime

CYBERSEC_EMAIL = "CyberSecurity@cswg.com"


def build_incident_mailto(
    reference: str,
    incident_type: str,
    description: str,
    urgency: str,
    sender_email: str = "",
    department: str = None,
    role: str = None,
) -> str:
    """Build a mailto: URL for an incident report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = f"[{urgency.upper()}] Security Incident Report {reference}"

    body = f"""Hi Cybersecurity Team,

I'm reporting a security incident via Fiona.

Reference:     {reference}
Date/Time:     {timestamp}
Urgency:       {urgency.upper()}
Incident Type: {incident_type.replace('_', ' ').title()}
Department:    {department or 'Not specified'}
Role:          {role or 'Not specified'}
Reporter:      {sender_email or 'Not provided'}

--- Description ---
{description}

---
Submitted via Fiona (C&S Cybersecurity Assistant).
"""

    return _build_mailto(CYBERSEC_EMAIL, subject, body)


def build_escalation_mailto(
    reference: str,
    query: str,
    conversation_context: str = "",
    sender_email: str = "",
    department: str = None,
    role: str = None,
) -> str:
    """Build a mailto: URL for an escalation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = f"[ESCALATION] {reference} — Question from {department or 'Employee'}"

    body = f"""Hi Cybersecurity Team,

I need human help with a question that Fiona couldn't fully answer.

Reference:     {reference}
Date/Time:     {timestamp}
Department:    {department or 'Not specified'}
Role:          {role or 'Not specified'}
Reporter:      {sender_email or 'Not provided'}

--- My Question ---
{query}

--- Conversation Context ---
{conversation_context or 'N/A'}

---
Submitted via Fiona (C&S Cybersecurity Assistant).
"""

    return _build_mailto(CYBERSEC_EMAIL, subject, body)


def _build_mailto(to: str, subject: str, body: str) -> str:
    return (
        f"mailto:{to}"
        f"?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )
