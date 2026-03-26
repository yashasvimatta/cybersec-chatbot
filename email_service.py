"""
Email service for Fiona — builds mailto: links that open the user's email client
with a pre-filled incident report or escalation addressed to CyberSecurity@cswg.com.
"""
import urllib.parse
from datetime import datetime

CYBERSEC_EMAIL = "CyberSecurity@cswg.com"


def _sanitize(value: str) -> str:
    """
    Strip characters that could inject additional email headers or break the
    mailto: URL.  Newlines are the primary injection vector (they let an
    attacker add BCC:/CC: headers); we replace them with a space.
    """
    if not value:
        return value
    return value.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').strip()


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

    # Sanitize all user-supplied fields before embedding in email headers/body
    urgency      = _sanitize(urgency or "medium")
    incident_type = _sanitize(incident_type or "")
    department   = _sanitize(department or "Not specified")
    role         = _sanitize(role or "Not specified")
    sender_email = _sanitize(sender_email or "Not provided")
    # description may contain newlines intentionally in the body — keep them,
    # but strip any leading/trailing whitespace
    description  = (description or "").strip()

    subject = f"[{urgency.upper()}] Security Incident Report {reference}"

    body = f"""Hi Cybersecurity Team,

I'm reporting a security incident via Fiona.

Reference:     {reference}
Date/Time:     {timestamp}
Urgency:       {urgency.upper()}
Incident Type: {incident_type.replace('_', ' ').title()}
Department:    {department}
Role:          {role}
Reporter:      {sender_email}

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

    department   = _sanitize(department or "Employee")
    role         = _sanitize(role or "Not specified")
    sender_email = _sanitize(sender_email or "Not provided")

    subject = f"[ESCALATION] {reference} — Question from {department}"

    body = f"""Hi Cybersecurity Team,

I need human help with a question that Fiona couldn't fully answer.

Reference:     {reference}
Date/Time:     {timestamp}
Department:    {department}
Role:          {role}
Reporter:      {sender_email}

--- My Question ---
{(query or "").strip()}

--- Conversation Context ---
{(conversation_context or "N/A").strip()}

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
