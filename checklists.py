"""
Security checklists by department / scenario.
"""

CHECKLISTS = {
    "new_employee": {
        "title": "New Employee Security Setup",
        "description": "Complete these steps to ensure your workstation and accounts are properly secured.",
        "departments": None,  # all departments
        "items": [
            "Set up Multi-Factor Authentication (MFA) on all company accounts",
            "Complete the Security Awareness Training module",
            "Set a strong, unique password (12+ characters, mix of types)",
            "Install company-approved antivirus/endpoint protection",
            "Configure automatic screen lock (5 minutes idle)",
            "Set up the corporate VPN on your device",
            "Review and acknowledge the Acceptable Use Policy",
            "Review and acknowledge the Data Classification Policy",
            "Bookmark the IT Service Desk portal for support requests",
            "Save the Cybersecurity Team's contact info for incident reporting",
        ],
    },
    "quarterly_access_review": {
        "title": "Quarterly Access Review",
        "description": "Review access permissions for your team's systems and shared resources.",
        "departments": ["IS", "Finance", "HR", "Procurement"],
        "items": [
            "Export current user access lists for all team systems",
            "Identify users who have left or changed roles",
            "Submit access revocation requests for departed users",
            "Review shared drive/folder permissions",
            "Check for dormant accounts (no login in 90+ days)",
            "Verify vendor/third-party access is still needed",
            "Document any exceptions and get manager approval",
            "Submit completed review to IS Security team",
        ],
    },
    "incident_response": {
        "title": "Incident Response Checklist",
        "description": "Steps to follow if you suspect or confirm a security incident.",
        "departments": None,
        "items": [
            "Do NOT turn off your computer or delete anything",
            "Disconnect from the network (unplug Ethernet / disable Wi-Fi)",
            "Note the exact time you noticed the incident",
            "Document what you observed (screenshots if possible)",
            "Contact the IT Service Desk immediately",
            "Do not discuss the incident on public channels (email/chat)",
            "Preserve any suspicious emails — do not forward or delete",
            "Follow instructions from the Cybersecurity Team",
            "Complete an incident report via Fiona or the portal",
        ],
    },
    "vendor_security": {
        "title": "Vendor Security Assessment",
        "description": "Before onboarding a new vendor with data access, complete this checklist.",
        "departments": ["Procurement", "IS", "Legal", "Supply Chain"],
        "items": [
            "Request the vendor's SOC 2 or ISO 27001 certification",
            "Review the vendor's security policies and incident history",
            "Ensure the contract includes security clauses and SLAs",
            "Define and document the minimum access the vendor needs",
            "Verify the vendor has adequate cyber insurance",
            "Set up separate credentials (no shared accounts)",
            "Schedule access expiration / periodic review dates",
            "Confirm the vendor's data handling meets our classification policy",
            "Get sign-off from IS Security and Legal",
        ],
    },
    "remote_work": {
        "title": "Remote Work Security",
        "description": "Ensure your home office setup meets security standards.",
        "departments": None,
        "items": [
            "Home Wi-Fi is password-protected (WPA3 or WPA2)",
            "Corporate VPN is installed and active during work",
            "Automatic OS and software updates are enabled",
            "Screen lock is set to activate after 5 minutes",
            "Work device is not shared with family members",
            "Sensitive documents are stored on company cloud, not local",
            "Physical workspace prevents shoulder surfing",
            "Company-approved video conferencing tools are installed",
        ],
    },
    "data_handling": {
        "title": "Sensitive Data Handling",
        "description": "Follow these steps when working with Confidential or Restricted data.",
        "departments": ["Finance", "HR", "Legal", "ELT"],
        "items": [
            "Classify the data according to the Data Classification Policy",
            "Use encryption for files at rest and in transit",
            "Share only through approved, encrypted channels",
            "Apply least-privilege access — only people who need it",
            "Never send sensitive data via personal email or chat",
            "Redact PII when full data isn't required",
            "Set expiration dates on shared links",
            "Log and track who accessed the data",
            "Securely delete data when no longer needed",
        ],
    },
}


def get_checklists_for_department(department: str = None) -> list:
    """Return checklists relevant to a department."""
    result = []
    for key, checklist in CHECKLISTS.items():
        depts = checklist.get("departments")
        if depts is None or (department and department in depts):
            result.append({
                "id": key,
                "title": checklist["title"],
                "description": checklist["description"],
                "items": checklist["items"],
                "total": len(checklist["items"]),
            })
    return result
