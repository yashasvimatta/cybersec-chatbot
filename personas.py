"""
Persona definitions for Fiona - C&S Cybersecurity Chatbot
Maps job titles from Active Directory to cybersecurity personas.
8 Business Units x 3-4 archetypes each = 28 total archetypes.
"""

PERSONAS = {
    "Supply Chain": {
        "icon": "🚛",
        "description": "Secure logistics, warehouse operations, and transportation systems against disruption and cyber threats.",
        "archetypes": [
            {
                "id": "sc_warehouse_floor",
                "name": "Warehouse Floor Worker",
                "description": "Hands-on warehouse operations — picking, packing, receiving, and shipping.",
                "systems": ["WMS (Warehouse Management System)", "Handheld scanners / RF devices", "Shared workstations", "Time & attendance terminals"],
                "threats": ["Phishing on shared devices", "USB drops in warehouse", "Tailgating & physical access", "Social engineering by phone"],
                "tone": "Plain, practical language. No jargon. Step-by-step instructions. Focus on immediate action.",
                "job_titles": [
                    "Selector", "Selector, Hourly", "Selector, Incentive", "Forklift Operator",
                    "Operator, Forklift", "Loader", "Lumper", "Porter", "Pallet Lead",
                    "Cell Operator", "Warehouse Athlete", "Generalist, Warehouse",
                    "Cross Dock", "Production Lead", "Backhauler/Unloader, Hourly",
                    "Backhauler/Unloader, Incentive", "Shipping Lead", "Receiving Lead",
                    "Receiver/Checker", "Clerk, Shipping", "Clerk, Receiving",
                    "Tote Washer", "Sanitation", "Utility", "Repack Selector",
                    "Pallet Sorter", "Mission Control Operator", "Warehouse Lead",
                    "Slotter", "Trainer",
                ],
                "use_cases": [
                    "What to do if I receive a suspicious email on a shared PC",
                    "How to report something suspicious in the warehouse",
                    "Safe use of shared devices and terminals",
                    "Physical security — tailgating and badge access",
                ],
            },
            {
                "id": "sc_supervisor",
                "name": "Warehouse Supervisor / Manager",
                "description": "Oversees warehouse shifts, teams, and operational systems.",
                "systems": ["WMS", "Shift scheduling tools", "Email & reporting tools", "Safety management systems"],
                "threats": ["Business email compromise", "Unauthorized system access by staff", "Phishing targeting managers", "Insider threats"],
                "tone": "Practical, operational. Balance between technical and non-technical. Focus on team impact and procedures.",
                "job_titles": [
                    "Warehouse Supervisor", "Warehouse Operations Mgr", "Warehouse Operations Mgr A",
                    "Mgr, Warehouse Shift Ops", "Warehouse EHS Manager", "Warehouse EHS Supervisor",
                    "Supv, Facility Training", "Mgr, Warehouse Support Services",
                    "Mgr, Operations Training", "Safety Manager", "ICQA Lead", "ICQA Specialist",
                    "Supv, ICQA", "Mgr, ICQA", "ICQA Auditor",
                ],
                "use_cases": [
                    "Managing staff access to warehouse systems",
                    "Responding to a suspected security incident in my team",
                    "Security training for warehouse floor staff",
                    "Handling a suspicious email targeting managers",
                ],
            },
            {
                "id": "sc_transport",
                "name": "Transportation & Logistics",
                "description": "Route planning, fleet management, dispatching, and inbound/outbound logistics.",
                "systems": ["TMS (Transportation Management System)", "Route planning tools", "Fleet tracking / telematics", "Dispatcher systems", "Email"],
                "threats": ["GPS spoofing / fleet tracking attacks", "Vendor impersonation", "Data breaches in logistics systems", "Ransomware targeting TMS"],
                "tone": "Operational focus. Relate security to logistics continuity and delivery reliability.",
                "job_titles": [
                    "Router I", "Router II", "Router III", "Senior Router",
                    "Dispatcher", "Transportation Coordinator", "Mgr, Transportation",
                    "Mgr, Fleet", "Mgr, Fleet Maintenance", "Mgr, Logistics",
                    "Mgr, Routing", "Regnl Mgr, Transportation", "Regional Manager, Transportation",
                    "Transportation Rep II", "Transportation Rep III", "Driver",
                    "Coordinator, Transportation", "Supv, Transportation",
                    "Supv, Driver/Dispatch", "Fleet Resource Coordinator",
                ],
                "use_cases": [
                    "Securing fleet management and GPS tracking systems",
                    "Vendor impersonation and freight fraud prevention",
                    "Safe use of TMS and routing tools",
                    "Reporting suspicious activity in logistics systems",
                ],
            },
            {
                "id": "sc_leadership",
                "name": "Supply Chain Director / VP",
                "description": "Strategic leadership of distribution, operations, and supply chain networks.",
                "systems": ["ERP", "Business intelligence dashboards", "Executive reporting tools", "Email"],
                "threats": ["Spear phishing targeting executives", "Third-party/vendor risk", "Business continuity threats", "Supply chain cyber attacks"],
                "tone": "Executive-level. Strategic framing, risk/business impact focus, concise summaries.",
                "job_titles": [
                    "VP, Distribution Operations", "VP,  Distribution Operations",
                    "VP, Distribution Operations - Mid-Atlantic", "VP, Distribution Operations - Midwest",
                    "SVP, Distribution Operations", "Sr Director, Distribution Operations - Southwest",
                    "Dir, Operations", "Sr Dir, Operations", "Sr Dir, Operations Strategy",
                    "EVP, Chief Supply Chain Officer", "Chief Executive Officer",
                    "Asst Dir, Operations", "Sr Dir, Planning & Logistics",
                ],
                "use_cases": [
                    "Executive-level cybersecurity risk briefings",
                    "Third-party and vendor security risk",
                    "Business continuity planning for cyber incidents",
                    "Supply chain attack surface and resilience",
                ],
            },
        ],
    },

    "Commercial": {
        "icon": "💼",
        "description": "Safeguard customer relationships, contracts, and commercial data while maintaining secure communication channels.",
        "archetypes": [
            {
                "id": "com_sales",
                "name": "Sales Representative",
                "description": "Customer-facing sales, account management, and business development.",
                "systems": ["CRM", "Email & calendar", "Mobile devices", "Customer portals"],
                "threats": ["Phishing targeting customer data", "Business email compromise", "Credential theft for CRM", "Data leakage via email"],
                "tone": "Friendly, practical. Connect security to protecting customer trust and deal data.",
                "job_titles": [
                    "Account Executive", "Account Exec, Chain Sales", "Account Exec, West Coast",
                    "Account Exec,Foodservice Sales", "Sr Account Executive", "Sr Account Exec, Chain Sales",
                    "Associate Account Executive", "Account Manager", "Sr Account Manager",
                    "Assoc Account Manager", "Inside Sales Rep", "Manager, Inside Sales",
                    "Commissioned Salesperson", "NE Salesperson", "MA Salesperson",
                    "CT Salesperson", "RI Salesperson", "Metro Salesperson",
                    "Representative, Perishable Sales", "Perishable Sales Specialist",
                ],
                "use_cases": [
                    "Secure email communication with customers and partners",
                    "Protecting CRM access and customer data",
                    "Recognizing business email compromise targeting sales",
                    "Safe use of mobile devices for customer work",
                ],
            },
            {
                "id": "com_merch",
                "name": "Merchandising & Category",
                "description": "Category management, merchandising, pricing, and product placement.",
                "systems": ["Merchandising systems", "Pricing tools", "Email", "Shared drives"],
                "threats": ["Data leakage of pricing/contracts", "Unauthorized access to merchandising data", "Phishing targeting category teams"],
                "tone": "Practical. Connect security to protecting pricing, contracts, and vendor information.",
                "job_titles": [
                    "Category Manager", "Sr Category Manager", "Category Merchandiser",
                    "Sr Category Merchandiser", "Category Development Manager",
                    "Sr Category Development Manager", "Center Store Category Specialist",
                    "Sr Center Store Category Specialist", "Reset Merchandiser",
                    "Merchandising Assistant II", "Merchandising Assistant III",
                    "Supervisor, Reset", "Supv, Reset", "Supv, Merchandising",
                    "Mgr, Reset", "Mgr, Merchandising", "Mgr, Category Sales",
                ],
                "use_cases": [
                    "Protecting pricing and contract data from unauthorized access",
                    "Secure file sharing with vendors and suppliers",
                    "Data classification for merchandising documents",
                    "Access control for category management systems",
                ],
            },
            {
                "id": "com_customer_exp",
                "name": "Customer Experience & Service",
                "description": "Customer support, service resolution, and relationship management.",
                "systems": ["Customer service platforms", "CRM", "Email", "Phone systems"],
                "threats": ["Social engineering by callers", "Phishing", "Unauthorized data access", "Credential sharing"],
                "tone": "Friendly and practical. Emphasize verification procedures and customer data protection.",
                "job_titles": [
                    "Customer Experience Manager", "Associate Customer Experience Manager",
                    "Mgr, Customer Experience", "Sr Mgr, Customer Experience",
                    "Dir, Customer Experience", "Sr Dir, Customer Experience",
                    "Customer Service Rep II", "Customer Service Rep III",
                    "Mgr, Customer Service", "Mgr, Customer Solutions",
                    "Liaison, Customer Operations",
                ],
                "use_cases": [
                    "Verifying caller identity before sharing account information",
                    "Protecting customer data in service interactions",
                    "Recognizing social engineering attempts over the phone",
                    "Reporting suspicious customer requests",
                ],
            },
            {
                "id": "com_leadership",
                "name": "Commercial Leadership",
                "description": "Senior commercial leadership overseeing sales, revenue, and market strategy.",
                "systems": ["ERP", "CRM", "Reporting tools", "Email"],
                "threats": ["Spear phishing", "Business email compromise", "Data breach of commercial data", "Vendor impersonation"],
                "tone": "Executive. Focus on risk to revenue, customer trust, and regulatory exposure.",
                "job_titles": [
                    "VP, General Manager", "SVP, General Manager", "Sr Dir, Customer Experience",
                    "Sr Dir, Retail Operations", "Senior Director, Sales & Merchandising",
                    "Regnl Mgr, Piggly Wiggly Sales", "District Manager", "NE District Manager",
                    "MA District Manager", "RI District Manager",
                ],
                "use_cases": [
                    "Managing data breach risk for commercial operations",
                    "Cybersecurity due diligence for business partnerships",
                    "Protecting executive communications from interception",
                    "Customer data protection and privacy compliance",
                ],
            },
        ],
    },

    "HR": {
        "icon": "👥",
        "description": "Protect employee data, manage security awareness training, and handle access during onboarding/offboarding.",
        "archetypes": [
            {
                "id": "hr_bp_recruiter",
                "name": "HR Business Partner / Recruiter",
                "description": "Employee relations, recruitment, talent acquisition, and workforce management.",
                "systems": ["HRIS (Workday)", "ATS (Applicant Tracking System)", "Email", "Background check portals"],
                "threats": ["Fake job applicants / recruitment fraud", "Phishing targeting HR teams", "PII leakage in hiring process", "Business email compromise"],
                "tone": "Practical. Connect security to protecting employee and candidate data (PII).",
                "job_titles": [
                    "HR Business Partner", "HR Business Partner - Field",
                    "Assoc, HR Business Partner", "Assoc, HR Business Partner - Field",
                    "Associate HR Business Partner", "HR Representative",
                    "Recruiter", "Sr Recruiter", "Associate Recruiter",
                    "Coordinator, Talent Acquisition", "Program Mgr, Talent Acquisition",
                    "Mgr, Talent Acquisition", "Sr Mgr, Talent Acquisition",
                    "VP, Talent Acquisition", "ERC Representative I", "ERC Representative II",
                ],
                "use_cases": [
                    "Protecting candidate and employee PII during recruitment",
                    "Recognizing fake job applicants and recruitment fraud",
                    "Secure handling of background check and reference data",
                    "Safe email practices when handling employee records",
                ],
            },
            {
                "id": "hr_operations",
                "name": "HR Operations & Benefits",
                "description": "Payroll, benefits administration, HR systems, and workforce operations.",
                "systems": ["HRIS", "Payroll systems", "Benefits portals", "Leave management systems"],
                "threats": ["Payroll fraud / diversion", "Benefits fraud", "PII data breach", "Unauthorized access to HRIS"],
                "tone": "Process-focused. Emphasize data protection for sensitive HR data and payroll security.",
                "job_titles": [
                    "HR Operations Specialist", "Analyst, HR Operations",
                    "Analyst, Human Resource Systems", "Analyst, Operations Compensation",
                    "Sr Analyst, HR", "Sr Analyst, HR Systems",
                    "Benefits Analyst", "Sr Analyst, Benefits",
                    "Leave of Absence Specialist", "Program Mgr, HR Ops",
                    "Supv, HR Operations", "Mgr, Benefits Admin",
                    "Payroll Systems Admin IV", "Principal, HCM Solutions",
                ],
                "use_cases": [
                    "Protecting payroll systems from fraud and diversion",
                    "Secure handling of benefits and compensation data",
                    "HRIS access control and data governance",
                    "Responding to unauthorized access of employee records",
                ],
            },
            {
                "id": "hr_leadership",
                "name": "HR Leadership",
                "description": "Strategic HR leadership, organizational development, and people strategy.",
                "systems": ["HRIS", "Executive reporting", "Email", "Compliance tools"],
                "threats": ["Spear phishing targeting HR leaders", "Data breach of employee records", "Insider threat", "Regulatory compliance failures"],
                "tone": "Strategic. Focus on risk to employee trust, regulatory compliance (GDPR, state privacy laws), and organizational impact.",
                "job_titles": [
                    "VP, Human Resources", "Sr Dir, HR Business Partner",
                    "SVP, Total Rewards & Shared Services", "Dir, HR Business Partner",
                    "Sr Dir, Talent Management", "Sr Dir, Compensation",
                    "Sr Dir, Total Rewards", "Mgr, HR Business Partner",
                    "Sr Mgr, HR Business Partner", "Senior Director, Transformation and Organizational Development",
                    "EVP, Human Resources",
                ],
                "use_cases": [
                    "Managing data breach notification for employee records",
                    "Insider threat program and employee monitoring policies",
                    "Privacy compliance for employee data (state laws, GDPR)",
                    "Cybersecurity awareness training strategy",
                ],
            },
        ],
    },

    "Legal": {
        "icon": "⚖️",
        "description": "Navigate cybersecurity regulations, data privacy laws, and incident response legal obligations.",
        "archetypes": [
            {
                "id": "legal_compliance",
                "name": "Compliance & Regulatory",
                "description": "Regulatory compliance, food safety, environmental, and OSHA compliance.",
                "systems": ["Compliance management systems", "Document management", "Email"],
                "threats": ["Regulatory data breaches", "Unauthorized access to compliance records", "Phishing targeting compliance teams"],
                "tone": "Precise and compliance-focused. Reference regulations and frameworks where relevant.",
                "job_titles": [
                    "Coordinator, Regulatory Compliance", "Principal, Regulatory Compliance",
                    "Sr Dir, Regulatory Compliance", "Retail Specialist, Food Safety",
                    "Dir, Environment & OSHA Compl", "Sr Mgr, Corp Food Safety",
                    "Specialist, Corp Food Safety", "Analyst, AA/EEO Data",
                    "Sr Business Continuity Manager",
                ],
                "use_cases": [
                    "Data privacy regulations and compliance obligations",
                    "Security requirements in vendor contracts and agreements",
                    "Breach notification timelines and regulatory requirements",
                    "Cybersecurity frameworks (NIST, ISO 27001) and compliance",
                ],
            },
            {
                "id": "legal_attorney",
                "name": "Attorney / Legal Counsel",
                "description": "Corporate legal affairs, labor law, litigation, and contract management.",
                "systems": ["Document management", "Legal research tools", "Email", "eDiscovery systems"],
                "threats": ["Attorney-client privilege breaches", "eDiscovery data security", "Phishing targeting legal teams", "Ransomware on legal files"],
                "tone": "Professional and precise. Reference legal obligations, privilege, and risk exposure.",
                "job_titles": [
                    "Sr Staff Attorney", "Corporate Legal Affairs Manager",
                    "Sr Dir, Corporate Law", "Sr Dir, Labor & Employment Law",
                    "Sr Dir, Labor & Employment", "Risk and Litigation Manager",
                    "Sr Paralegal", "Real Estate Manager", "Sr Analyst, Legal",
                    "Sr Dir, Risk & Litigation",
                ],
                "use_cases": [
                    "Attorney-client privilege and cybersecurity incident response",
                    "Legal hold and eDiscovery data security",
                    "Data breach legal obligations and notification requirements",
                    "Cybersecurity contract clauses and vendor agreements",
                ],
            },
            {
                "id": "legal_leadership",
                "name": "Legal & Risk Leadership",
                "description": "Chief legal officer, VP-level legal and risk leadership.",
                "systems": ["Executive tools", "Legal management systems", "Email"],
                "threats": ["Executive-targeted phishing", "Corporate espionage", "Regulatory enforcement risk", "Reputational risk from breaches"],
                "tone": "Executive. Focus on legal liability, regulatory risk, and strategic risk management.",
                "job_titles": [
                    "VP, Labor & Employment Law", "VP, Operations Law & Real Estate",
                    "VP, Labor Relations", "SVP, Compliance & Admin",
                    "EVP, Chief Legal Officer",
                ],
                "use_cases": [
                    "Legal liability and regulatory risk from cyber incidents",
                    "Board-level cybersecurity governance and oversight",
                    "M&A cybersecurity due diligence",
                    "Insurance coverage for cyber incidents",
                ],
            },
        ],
    },

    "IS/IT": {
        "icon": "🛡️",
        "description": "Your command center — manage incidents, enforce policies, monitor threats, and maintain the security posture of the organization.",
        "archetypes": [
            {
                "id": "is_support",
                "name": "IT Support & Security Operations",
                "description": "Help desk, desktop support, field support, and security operations.",
                "systems": ["Ticketing systems (ServiceNow)", "Active Directory", "Endpoint management tools", "SIEM", "Email"],
                "threats": ["Social engineering targeting helpdesk", "Credential reset abuse", "Malware on endpoints", "Phishing escalations from users"],
                "tone": "Technical but accessible. Step-by-step. Focus on operational procedures and escalation paths.",
                "job_titles": [
                    "Systems Administrator", "Regional Field Support Tech",
                    "Retail Help Desk Rep II", "Retail Help Desk Rep IV",
                    "Retail Support Technician III", "Retail Support Technician IV",
                    "Retail Support Tech IV", "Field Support Tech III",
                    "Security Guard", "Sr Coordinator, Security",
                    "Analyst, IS Security and Compliance", "IS Service Delivery Manager",
                    "Engineer, IT Admin", "Principal Engineer, IT Admin",
                ],
                "use_cases": [
                    "Verifying user identity before password resets",
                    "Escalating suspected phishing and malware incidents",
                    "Endpoint security and patch management",
                    "Handling users who clicked suspicious links",
                ],
            },
            {
                "id": "is_engineer",
                "name": "Engineer / Developer",
                "description": "Application development, network engineering, database administration, and system integrations.",
                "systems": ["Dev environments", "Cloud platforms (Azure/GCP/AWS)", "CI/CD pipelines", "Network infrastructure", "Databases"],
                "threats": ["Supply chain attacks on code", "Insecure APIs", "SQL injection / code vulnerabilities", "Cloud misconfigurations", "Credential exposure in code"],
                "tone": "Technical. Use precise security terminology. Reference CVEs, frameworks, and technical controls.",
                "job_titles": [
                    "Engineer, Network", "Sr Engineer, Network", "Sr Architect, Network",
                    "Engineer, Database Admin", "Principal Engineer, DBA",
                    "Developer, Web Application", "Sr Developer, Web Application",
                    "Sr. Developer, Web Application", "Assoc Engineer, App Development",
                    "Sr Engineer, App Development", "Automation Engineer",
                    "Sr Eng, Cloud", "Sr Eng, Software",
                    "Sr Engineer, IS Security", "Sr Engineer, System Integrations",
                    "Sr Engineer, Supply Chain Application Development",
                ],
                "use_cases": [
                    "Secure coding practices and OWASP top 10",
                    "API security and authentication best practices",
                    "Cloud security and misconfiguration risks",
                    "Secret management and credential security in code",
                ],
            },
            {
                "id": "is_architect",
                "name": "Architect / Senior Engineer",
                "description": "IT architecture, security architecture, principal engineers, and lead data scientists.",
                "systems": ["Enterprise architecture tools", "Cloud platforms", "Security platforms", "DevSecOps tooling"],
                "threats": ["Architecture-level security gaps", "Zero-day vulnerabilities", "Advanced persistent threats", "Third-party integration risks"],
                "tone": "Highly technical. Architecture and design patterns. Risk-based decision making.",
                "job_titles": [
                    "Architect, IT", "Sr Architect, IT", "Architect, App Development",
                    "Sr Architect, App Development", "Architect, Business Systems Analysis/ERP",
                    "Architect, Web Application", "Principal Engineer, App Development",
                    "Principal Engineer, App Dev", "Principal Engineer, Business Intelligence",
                    "Principal Engineer, Data Warehousing", "Principal Engineer, Sys Admin",
                    "Lead Data Scientist", "IT Project Manager", "Sr IT Project Manager",
                ],
                "use_cases": [
                    "Security architecture review and threat modeling",
                    "Zero trust architecture and network segmentation",
                    "Cloud security architecture and controls",
                    "DevSecOps and secure SDLC integration",
                ],
            },
            {
                "id": "is_leadership",
                "name": "IS/IT Leadership",
                "description": "CIO, CISO, VP of IS, and senior IS directors.",
                "systems": ["Executive dashboards", "Security risk platforms", "Enterprise architecture", "GRC tools"],
                "threats": ["Advanced persistent threats", "Ransomware", "Insider threats", "Third-party risk", "Regulatory non-compliance"],
                "tone": "Executive/strategic. Risk quantification, business impact, regulatory exposure, and governance.",
                "job_titles": [
                    "EVP, Chief Information Officer", "VP, IS Security and Service Delivery",
                    "VP, Information Systems", "VP, IS Infrastructure",
                    "VP, IS Commercial", "VP, IS Distribution Systems",
                    "Sr Dir, Security", "Dir, IS Security", "Sr Dir, App Development",
                    "Sr Dir, Web Application", "Sr Dir, IS PMO",
                    "SVP, IS E-Commerce & Digital Product",
                    "SVP, Infrastructure, Applications & Operations",
                ],
                "use_cases": [
                    "Security KPIs and executive-level reporting",
                    "Ransomware response and business continuity",
                    "Security budget justification and risk quantification",
                    "Regulatory compliance and audit readiness",
                ],
            },
        ],
    },

    "Finance": {
        "icon": "💰",
        "description": "Protect financial data, ensure compliance with SOX/PCI-DSS, and safeguard payment systems from fraud.",
        "archetypes": [
            {
                "id": "fin_ap_ar",
                "name": "Accounts Payable / Receivable",
                "description": "Processing payments, invoices, billing, and collections.",
                "systems": ["ERP (AP/AR modules)", "Banking portals", "Email", "Invoice processing systems"],
                "threats": ["Business email compromise targeting payments", "Fraudulent invoice schemes", "Phishing for banking credentials", "Vendor impersonation"],
                "tone": "Clear and practical. Focus on payment fraud prevention and verification procedures.",
                "job_titles": [
                    "Accounts Payable Rep II", "Accounts Payable Rep III",
                    "Accounts Receivable Rep I", "Accounts Receivable Rep II",
                    "Accounts Receivable Rep III", "AR Rep II Billing",
                    "AR Rep II Cash Application", "Collections Associate",
                    "AR Collections Analyst", "Payroll Specialist III",
                    "Payroll Specialist IV", "Payroll Administrator",
                ],
                "use_cases": [
                    "Preventing payment fraud and business email compromise",
                    "Verifying vendor bank account change requests",
                    "Secure handling of payment and banking information",
                    "Recognizing fraudulent invoice and wire transfer requests",
                ],
            },
            {
                "id": "fin_analyst",
                "name": "Financial Analyst / Accountant",
                "description": "Financial reporting, analysis, tax, treasury, and accounting.",
                "systems": ["ERP", "Hyperion / financial reporting tools", "Excel / BI tools", "Email"],
                "threats": ["Data breaches of financial reports", "Phishing targeting financial credentials", "Unauthorized access to financial data", "Ransomware on financial systems"],
                "tone": "Professional. Connect security to financial data integrity, SOX compliance, and audit readiness.",
                "job_titles": [
                    "Financial Analyst", "Sr Financial Analyst", "Assoc Financial Analyst",
                    "Analyst, Accounting", "Sr Analyst, Accounting",
                    "Principal Analyst, Accounting", "Associate Accountant II",
                    "Accountant, External Reporting", "Sr Accountant, External Reporting",
                    "Analyst, Tax", "Sr Analyst, Tax", "Analyst, Treasury",
                    "Sr Analyst, Treasury", "Sr Analyst, Internal Audit",
                    "Internal Audit Representative",
                ],
                "use_cases": [
                    "Protecting financial data and reports from unauthorized access",
                    "SOX compliance and security controls for financial systems",
                    "Secure handling of sensitive financial information",
                    "Recognizing phishing targeting financial teams",
                ],
            },
            {
                "id": "fin_manager",
                "name": "Finance Manager / Director",
                "description": "Accounting management, financial operations, payroll, and AP/AR management.",
                "systems": ["ERP", "Financial reporting", "Payroll systems", "Banking portals"],
                "threats": ["Payroll diversion fraud", "Business email compromise", "Insider financial fraud", "Unauthorized wire transfers"],
                "tone": "Management-focused. Risk to financial operations, audit, and regulatory compliance.",
                "job_titles": [
                    "Mgr, Accounting", "Mgr, Finance", "Manager, Finance",
                    "Dir, Accounting", "Dir, Payroll", "Mgr, Accounts Payable",
                    "Mgr, Collections", "Mgr, Financial Analysis",
                    "Mgr, Fin Planning & Analysis", "Dir, Fin Planning & Analysis",
                    "Mgr, External Reporting", "Dir, External Reporting",
                    "Mgr, Accounts Receivable", "Sr Mgr, Accounts Receivable",
                    "Mgr, Tax", "Director, Tax",
                ],
                "use_cases": [
                    "Preventing payroll diversion and payment fraud",
                    "Dual controls and separation of duties for financial transactions",
                    "Managing access to financial systems and banking portals",
                    "Responding to suspected financial fraud incidents",
                ],
            },
            {
                "id": "fin_leadership",
                "name": "Finance Leadership",
                "description": "CFO, VP Finance, and senior finance leadership.",
                "systems": ["Executive dashboards", "ERP", "Banking systems", "Board reporting"],
                "threats": ["CEO/CFO fraud (whaling)", "Wire transfer fraud", "Financial data breach", "Ransomware on financial systems"],
                "tone": "Executive. Risk to financial operations, regulatory exposure, reputational impact, and fiduciary duty.",
                "job_titles": [
                    "VP, Finance", "VP, Finance Corporate Controller",
                    "VP, Internal Audit", "VP, Tax", "VP, Assistant Treasurer",
                    "EVP, Chief Financial Officer",
                    "SVP, Corporate Development & Financial Planning",
                ],
                "use_cases": [
                    "CEO/CFO fraud prevention and wire transfer controls",
                    "Financial cybersecurity risk governance",
                    "SOX and PCI-DSS compliance oversight",
                    "Cyber insurance and financial risk quantification",
                ],
            },
        ],
    },

    "Procurement": {
        "icon": "📦",
        "description": "Manage vendor cybersecurity risk, secure procurement platforms, and protect contract and pricing data.",
        "archetypes": [
            {
                "id": "proc_buyer",
                "name": "Buyer / Merchandiser",
                "description": "Procurement of goods, vendor negotiations, and category management.",
                "systems": ["Procurement systems", "Vendor portals", "Email", "Pricing tools"],
                "threats": ["Vendor impersonation", "Fraudulent pricing communications", "Phishing targeting buyers", "Data leakage of pricing/contracts"],
                "tone": "Practical. Connect security to protecting vendor relationships and procurement data.",
                "job_titles": [
                    "Buyer", "Sr Buyer", "Sr Buyer, Fresh", "Sr Buyer, Perishable",
                    "Sr Buyer, Perishables", "National Buyer", "National Buyer, Perishables",
                    "Buyer, Perishables", "Buyer/Merchandiser", "Sr Buyer/Merchandiser",
                    "Associate Buyer", "Buyer Assistant II", "Buyer Assistant III",
                    "National Category Mgr", "Sr Category Manager",
                ],
                "use_cases": [
                    "Verifying vendor communications before changing payment details",
                    "Protecting pricing and contract data from unauthorized access",
                    "Safe communication with vendors via email and portals",
                    "Recognizing vendor impersonation and procurement fraud",
                ],
            },
            {
                "id": "proc_planning",
                "name": "Demand Planning & Inventory",
                "description": "Demand forecasting, inventory management, supply chain planning, and scheduling.",
                "systems": ["Demand planning tools", "Inventory management systems", "ERP", "Analytics tools"],
                "threats": ["Data manipulation in planning systems", "Unauthorized access to inventory data", "Phishing targeting planning teams", "Ransomware on supply chain systems"],
                "tone": "Systems-focused. Connect security to data integrity for planning accuracy.",
                "job_titles": [
                    "Demand Planning Analyst", "Sr Demand Planner",
                    "Demand Planning Rep II", "Demand Planning Rep III",
                    "Inventory Control Specialist", "Inventory Control Rep III",
                    "Inventory Control Lead", "Scheduling Rep I", "Scheduling Rep II",
                    "Analyst, Inventory Control", "Analyst, Capacity Planning",
                    "Team Lead, Demand Planning", "Director, Demand Planning",
                ],
                "use_cases": [
                    "Data integrity and security for demand planning systems",
                    "Protecting inventory data from unauthorized access or manipulation",
                    "Secure access to ERP and planning tools",
                    "Reporting anomalies in planning system data",
                ],
            },
            {
                "id": "proc_manager",
                "name": "Procurement Manager",
                "description": "Procurement operations management, vendor relations, and contract administration.",
                "systems": ["Procurement platforms", "Vendor management systems", "Contract management", "ERP"],
                "threats": ["Vendor account takeover", "Contract data theft", "Business email compromise", "Third-party risk"],
                "tone": "Management-focused. Third-party risk, vendor security, and procurement process integrity.",
                "job_titles": [
                    "Mgr, Procurement", "Dir, Procurement", "Sr Dir, Procurement",
                    "Dir, Fresh Procurement", "Mgr, Fresh Procurement",
                    "MGR, FRESH PROCUREMNT", "Sr Mgr, Procurement",
                    "Mgr, National Logistics", "Mgr, Supply Chain Analytics",
                    "Sr Project Manager, Procurement", "Supv, Procurement",
                ],
                "use_cases": [
                    "Vendor security assessments and third-party risk",
                    "Protecting procurement data and contracts from unauthorized access",
                    "Managing vendor portal access and permissions",
                    "Responding to suspected vendor fraud incidents",
                ],
            },
            {
                "id": "proc_leadership",
                "name": "Procurement Leadership",
                "description": "Chief Procurement Officer and VP-level procurement leadership.",
                "systems": ["Executive tools", "Enterprise procurement platforms", "Vendor risk management"],
                "threats": ["Supply chain cyber attacks", "Third-party vendor breaches", "Strategic pricing data theft", "Executive phishing"],
                "tone": "Executive. Strategic vendor risk, supply chain resilience, and regulatory compliance.",
                "job_titles": [
                    "VP, Procurement&Merchandising", "VP, Non-Perishable Procurement",
                    "VP, Fresh Procurement", "SVP, Fresh Procurement",
                    "VP, Produce Ops/Procurement", "VP, Dairy",
                    "VP, Fresh&Packaged Meat Ops", "VP, Procurement Integration",
                    "EVP, Chief Procurement Officer",
                ],
                "use_cases": [
                    "Strategic vendor cybersecurity risk management",
                    "Supply chain attack resilience and continuity",
                    "Third-party security requirements in contracts",
                    "Procurement data governance and privacy compliance",
                ],
            },
        ],
    },

    "Retail": {
        "icon": "🛒",
        "description": "Protect point-of-sale systems, customer data, and store operations from cyber threats.",
        "archetypes": [
            {
                "id": "ret_store_ops",
                "name": "Store Operations",
                "description": "Store managers, pharmacists, and retail operations staff.",
                "systems": ["POS systems", "Store management systems", "Email", "Shared store computers"],
                "threats": ["POS skimming and tampering", "Social engineering at store level", "Phishing on store devices", "Physical security breaches"],
                "tone": "Practical and direct. Focus on what to look for and what to do at the store level.",
                "job_titles": [
                    "Store Mgr", "Pharmacist", "Reset Merchandiser",
                    "Retail Sales Counselor", "Sr Retail Sales Counselor",
                    "Retail Sales Merchandiser", "CT PT Merchandiser",
                    "Retail Development Manager", "Retail Pricing Coordinator",
                    "Retail Pricing Coordinator II",
                ],
                "use_cases": [
                    "Identifying POS tampering and skimming devices",
                    "Physical security and access control at retail locations",
                    "Reporting suspicious customers or incidents",
                    "Safe use of shared store computers and devices",
                ],
            },
            {
                "id": "ret_merchandising",
                "name": "Retail Merchandising & Marketing",
                "description": "Category management, private brands, marketing, pricing, and promotional planning.",
                "systems": ["Merchandising systems", "Marketing platforms", "Digital tools", "Email"],
                "threats": ["Unauthorized access to pricing/promotional data", "Brand impersonation", "Phishing targeting marketing teams", "Data leakage"],
                "tone": "Practical. Connect security to protecting brand, pricing, and promotional data.",
                "job_titles": [
                    "Category Manager", "Analyst, Private Brands", "Sr Analyst, Our Brands",
                    "Merchandising Analyst", "Sr Category Merchandiser",
                    "Assoc Category Merchandiser", "Graphic Designer", "Graphics Technician",
                    "Marketing Associate", "Administrator, Marketing",
                    "Analyst, Promotional", "Analyst, Category Development",
                    "Independent Promotions Manager", "Mgr, Category Management",
                ],
                "use_cases": [
                    "Protecting pricing and promotional data from leakage",
                    "Secure use of digital marketing and creative tools",
                    "Brand protection and social media security",
                    "Data classification for retail documents",
                ],
            },
            {
                "id": "ret_leadership",
                "name": "Retail Leadership",
                "description": "VP and senior director-level retail leadership.",
                "systems": ["Executive dashboards", "Retail management platforms", "Email"],
                "threats": ["Executive phishing", "PCI-DSS compliance risk", "Customer data breach", "Reputational risk from retail incidents"],
                "tone": "Executive. Focus on PCI-DSS compliance, customer data protection, and brand risk.",
                "job_titles": [
                    "VP, Merchandising Non-Perish", "VP, Non-Perishable Procurement",
                    "SVP, NonPrshMrch& SC/Trde Rels", "Sr Dir, Merchandising",
                    "Sr Dir, Product Management", "EVP, Retail & Chief Merchandising Officer",
                    "Sr Mgr, Retail Innovation",
                ],
                "use_cases": [
                    "PCI-DSS compliance for retail operations",
                    "Customer data protection and privacy",
                    "Cyber incident impact on customer trust and brand",
                    "Retail cybersecurity governance and risk management",
                ],
            },
        ],
    },
}


def get_persona_from_job_title(job_title: str, business_unit: str = None) -> dict:
    """
    Match a job title to the best persona archetype.
    Returns: { business_unit, archetype_id, archetype_name, systems, threats, tone, ... }
    """
    if not job_title:
        return None

    job_lower = job_title.lower().strip()

    # If business_unit is provided, search within that BU first
    search_units = (
        [business_unit] + [k for k in PERSONAS if k != business_unit]
        if business_unit and business_unit in PERSONAS
        else list(PERSONAS.keys())
    )

    best_match = None
    best_score = 0

    for bu_name in search_units:
        bu = PERSONAS[bu_name]
        for archetype in bu["archetypes"]:
            for title in archetype["job_titles"]:
                title_lower = title.lower()
                # Exact match → return immediately
                if job_lower == title_lower:
                    return _build_result(bu_name, archetype, job_title)
                # Partial overlap score
                job_words = set(job_lower.split())
                title_words = set(title_lower.split())
                score = len(job_words & title_words)
                if score > best_score:
                    best_score = score
                    best_match = _build_result(bu_name, archetype, job_title)

    return best_match if best_score > 0 else None


def _build_result(bu_name: str, archetype: dict, job_title: str) -> dict:
    return {
        "business_unit": bu_name,
        "archetype_id": archetype["id"],
        "archetype_name": archetype["name"],
        "description": archetype["description"],
        "systems": archetype["systems"],
        "threats": archetype["threats"],
        "tone": archetype["tone"],
        "use_cases": archetype["use_cases"],
        "job_title": job_title,
    }


def build_persona_prompt_block(persona: dict) -> str:
    """
    Build a rich persona context block for LLM prompts.
    Works with both simple personas {department, role} and rich archetypes.
    """
    if not persona:
        return ""

    bu = persona.get("business_unit") or persona.get("department", "Unknown")
    archetype = persona.get("archetype_name") or persona.get("role", "Team Member")
    job_title = persona.get("job_title") or persona.get("role", "")
    systems = persona.get("systems", [])
    threats = persona.get("threats", [])
    tone = persona.get("tone", "")

    lines = ["\n**USER CONTEXT:**"]
    lines.append(f"- **Business Unit:** {bu}")
    if job_title and job_title != archetype:
        lines.append(f"- **Role:** {archetype} (Job title: {job_title})")
    else:
        lines.append(f"- **Role:** {archetype}")
    if systems:
        lines.append(f"- **Systems they use:** {', '.join(systems[:4])}")
    if threats:
        lines.append(f"- **Most relevant cyber threats for this role:** {', '.join(threats[:3])}")
    if tone:
        lines.append(f"\n**Response style:** {tone}")
    lines.append(
        f"\nTailor your answer specifically for this person. "
        f"Use examples and language relevant to {bu} operations. "
        f"Highlight what matters most to someone in the {archetype} role."
    )

    return "\n".join(lines)
