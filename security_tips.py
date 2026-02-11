"""
Daily security tips — rotated by date, optionally filtered by department.
"""
from datetime import date

TIPS = [
    {"tip": "**Phishing Alert:** Always hover over links before clicking. If the URL looks suspicious or doesn't match the sender's organization, don't click — report it to the Cybersecurity Team.", "category": "phishing", "departments": None},
    {"tip": "**Password Hygiene:** Use a unique, complex password for every system. Never reuse your C&S credentials on personal sites. Enable MFA wherever possible.", "category": "passwords", "departments": None},
    {"tip": "**Lock Your Screen:** Pressing `Win+L` (Windows) or `Ctrl+Cmd+Q` (Mac) locks your workstation instantly. Make it a habit every time you step away.", "category": "physical", "departments": None},
    {"tip": "**Secure File Sharing:** Only share files through approved company platforms. Avoid personal cloud storage (Dropbox, personal Google Drive) for work documents.", "category": "data", "departments": None},
    {"tip": "**USB Safety:** Never plug in unknown USB drives. They could contain malware. Report any found USB devices to IT.", "category": "physical", "departments": None},
    {"tip": "**Email Encryption:** When sending sensitive data (PII, financial info, contracts), always use the company-approved email encryption. Look for the \"Encrypt\" option in Outlook.", "category": "email", "departments": ["Finance", "Legal", "HR", "Procurement"]},
    {"tip": "**Social Engineering:** Be cautious of urgent phone calls or emails demanding immediate action, especially wire transfers or credential sharing. Verify through a separate channel.", "category": "social_engineering", "departments": ["Finance", "Commercial", "ELT"]},
    {"tip": "**Software Updates:** Keep your OS and applications updated. Security patches fix known vulnerabilities that attackers actively exploit.", "category": "updates", "departments": None},
    {"tip": "**Clean Desk Policy:** Don't leave sensitive documents, Post-it notes with passwords, or unlocked devices unattended. Secure physical documents in locked drawers.", "category": "physical", "departments": None},
    {"tip": "**Wi-Fi Safety:** Avoid using public Wi-Fi for work tasks. If you must, always connect through the company VPN first.", "category": "network", "departments": None},
    {"tip": "**Vendor Access:** Third-party vendors should have the minimum access needed. Review and revoke vendor access regularly — especially after projects end.", "category": "access", "departments": ["Procurement", "Supply Chain", "IS"]},
    {"tip": "**Data Classification:** Know the difference between Public, Internal, Confidential, and Restricted data. Handle each category according to our Data Classification Policy.", "category": "data", "departments": ["Legal", "Commercial", "Finance"]},
    {"tip": "**Incident Reporting:** If you see something suspicious, say something. Early reporting of a potential incident can prevent a breach. Use Fiona's Report Incident feature!", "category": "incident", "departments": None},
    {"tip": "**MFA is Essential:** Multi-Factor Authentication blocks 99.9% of automated attacks. If a system offers MFA, enable it. Don't share your MFA codes with anyone.", "category": "passwords", "departments": None},
    {"tip": "**Offboarding Security:** When an employee leaves, their access must be revoked within 24 hours. Managers: ensure you submit access revocation requests promptly.", "category": "access", "departments": ["HR", "IS"]},
    {"tip": "**Ransomware Prevention:** Don't open unexpected attachments. Keep backups current. If your system is behaving strangely (files encrypted, ransom notes), disconnect from the network and call IT immediately.", "category": "malware", "departments": None},
    {"tip": "**PCI Compliance:** Never store full credit card numbers in emails, spreadsheets, or chat. Use only PCI-compliant systems for payment processing.", "category": "compliance", "departments": ["Finance", "Retail", "Commercial"]},
    {"tip": "**Tailgating:** Don't hold doors open for people you don't recognize. Everyone should badge in. Politely ask unrecognized visitors to check in at reception.", "category": "physical", "departments": ["Retail", "Supply Chain"]},
    {"tip": "**Browser Safety:** Stick to business-related websites. If your browser warns you about a dangerous site, don't proceed. Report blocked sites through proper channels.", "category": "browsing", "departments": None},
    {"tip": "**Backup Your Work:** Save critical files to company-approved cloud storage, not just your local drive. Local drives aren't backed up — if your laptop fails, the data is gone.", "category": "data", "departments": None},
    {"tip": "**Remote Work Security:** Working from home? Ensure your home Wi-Fi is password-protected, your VPN is active, and family members don't have access to your work device.", "category": "remote", "departments": None},
    {"tip": "**Credential Sharing:** Never share your username, password, or MFA token — not even with IT support. Legitimate IT staff will never ask for your password.", "category": "passwords", "departments": None},
    {"tip": "**QR Code Caution:** Attackers now use malicious QR codes ('quishing'). Only scan QR codes from trusted sources. If a QR code arrives via email, verify the sender first.", "category": "phishing", "departments": None},
    {"tip": "**Access Reviews:** Regularly review who has access to your team's shared drives and tools. Remove people who no longer need access. Least privilege = least risk.", "category": "access", "departments": ["IS", "Finance", "HR"]},
    {"tip": "**Contract Security Clauses:** Every vendor contract should include cybersecurity requirements, incident notification obligations, and audit rights. Check with Legal if unsure.", "category": "compliance", "departments": ["Procurement", "Legal", "Commercial"]},
    {"tip": "**Security Awareness Training:** Complete your annual security awareness training on time. It's mandatory and helps you recognize the latest threats.", "category": "training", "departments": None},
    {"tip": "**POS System Security:** Never install unauthorized software on POS terminals. Report any POS device that looks tampered with immediately.", "category": "pos", "departments": ["Retail"]},
    {"tip": "**AI & Data Privacy:** Don't paste sensitive company data, PII, or credentials into public AI tools (ChatGPT, etc.). Use only company-approved AI tools like Fiona.", "category": "data", "departments": None},
    {"tip": "**VPN Always On:** When working outside the office, always connect through the corporate VPN before accessing any company systems or data.", "category": "network", "departments": None},
    {"tip": "**Reporting Wins:** Every phishing email you report helps protect your colleagues. The Cybersecurity Team uses these reports to block threats across the entire organization.", "category": "phishing", "departments": None},
]


def get_tip_of_the_day(department: str = None) -> dict:
    """Return today's tip, optionally filtered for relevance to a department."""
    today = date.today()
    day_index = today.toordinal()

    # Filter tips relevant to this department (or universal)
    if department:
        relevant = [t for t in TIPS if t["departments"] is None or department in t["departments"]]
    else:
        relevant = TIPS

    if not relevant:
        relevant = TIPS

    tip = relevant[day_index % len(relevant)]
    return {
        "tip": tip["tip"],
        "category": tip["category"],
        "date": today.isoformat(),
    }
