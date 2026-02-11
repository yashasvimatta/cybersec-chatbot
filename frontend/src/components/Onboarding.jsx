import React, { useState } from "react";

const DEPARTMENTS = {
  "Finance": {
    icon: "\uD83D\uDCB0",
    roles: [
      "CFO / VP Finance",
      "Controller",
      "Financial Analyst",
      "Accounts Payable / Receivable",
      "Treasury Manager",
      "Other",
    ],
    description:
      "Protect financial data, ensure compliance with SOX/PCI-DSS, and safeguard payment systems from fraud and cyber threats.",
    useCases: [
      "Identify risks to financial systems and payment processing",
      "Ensure compliance with data protection regulations",
      "Review access controls for sensitive financial data",
      "Understand phishing threats targeting finance teams",
    ],
  },
  "Supply Chain": {
    icon: "\uD83D\uDE9A",
    roles: [
      "VP Supply Chain",
      "Logistics Manager",
      "Warehouse Manager",
      "Transportation Coordinator",
      "Demand Planner",
      "Other",
    ],
    description:
      "Secure logistics platforms, vendor integrations, and warehouse systems against disruption and data breaches.",
    useCases: [
      "Assess cybersecurity risks in vendor/partner integrations",
      "Protect warehouse management and IoT systems",
      "Ensure business continuity during cyber incidents",
      "Review third-party access and data sharing policies",
    ],
  },
  "IS": {
    icon: "\uD83D\uDEE1\uFE0F",
    roles: [
      "CISO",
      "Security Analyst",
      "Network Engineer",
      "Systems Administrator",
      "IT Support / Help Desk",
      "Other",
    ],
    description:
      "Your command center — manage incidents, enforce policies, monitor threats, and maintain the security posture of the organization.",
    useCases: [
      "Look up security policies and incident response procedures",
      "Analyze vulnerability reports and pen test findings",
      "Review firewall rules and network security configurations",
      "Track KPIs and security awareness metrics",
    ],
  },
  "Retail": {
    icon: "\uD83D\uDED2",
    roles: [
      "Store Manager",
      "Regional Manager",
      "Merchandising Manager",
      "Loss Prevention Manager",
      "Operations Manager",
      "Other",
    ],
    description:
      "Protect point-of-sale systems, customer data, and store operations from cyber threats and social engineering.",
    useCases: [
      "Understand POS security and payment card protections",
      "Recognize social engineering and phishing attempts",
      "Report suspicious activity and security incidents",
      "Learn about physical and digital security best practices",
    ],
  },
  "Commercial": {
    icon: "\uD83D\uDCBC",
    roles: [
      "VP Commercial",
      "Sales Director",
      "Account Manager",
      "Business Development Manager",
      "Category Manager",
      "Other",
    ],
    description:
      "Safeguard customer relationships, contracts, and commercial data while maintaining secure communication channels.",
    useCases: [
      "Protect customer and deal data from unauthorized access",
      "Ensure secure file sharing with external partners",
      "Understand email security and communication policies",
      "Learn about data classification for commercial documents",
    ],
  },
  "Procurement": {
    icon: "\uD83D\uDCE6",
    roles: [
      "Chief Procurement Officer",
      "Procurement Manager",
      "Buyer / Senior Buyer",
      "Vendor Relations Manager",
      "Contract Specialist",
      "Other",
    ],
    description:
      "Manage vendor cybersecurity risk, secure procurement platforms, and protect contract and pricing data.",
    useCases: [
      "Evaluate vendor security posture and compliance",
      "Protect procurement systems and contract data",
      "Understand third-party risk assessment processes",
      "Review access management for procurement tools",
    ],
  },
  "Legal": {
    icon: "\u2696\uFE0F",
    roles: [
      "General Counsel",
      "Corporate Attorney",
      "Compliance Officer",
      "Paralegal",
      "Contract Manager",
      "Other",
    ],
    description:
      "Navigate cybersecurity regulations, data privacy laws, and incident response legal obligations.",
    useCases: [
      "Understand data breach notification requirements",
      "Review cybersecurity policies and compliance frameworks",
      "Assess legal implications of security incidents",
      "Ensure contracts include proper security clauses",
    ],
  },
  "HR": {
    icon: "\uD83D\uDC65",
    roles: [
      "CHRO / VP HR",
      "HR Business Partner",
      "Recruiter",
      "Benefits Administrator",
      "Training & Development Manager",
      "Other",
    ],
    description:
      "Protect employee data, manage security awareness training, and handle access during onboarding/offboarding.",
    useCases: [
      "Manage employee access rights and offboarding procedures",
      "Coordinate security awareness training programs",
      "Protect sensitive HR data (PII, benefits, payroll)",
      "Understand workstation security for remote employees",
    ],
  },
  "ELT": {
    icon: "\uD83C\uDFAF",
    roles: [
      "CEO",
      "COO",
      "CTO",
      "SVP Operations",
      "Chief Strategy Officer",
      "Other",
    ],
    description:
      "Strategic oversight of cybersecurity posture, risk management, and organizational resilience.",
    useCases: [
      "Get executive summaries of security posture and KPIs",
      "Understand organizational cyber risk and mitigation strategies",
      "Review incident response readiness and business continuity",
      "Assess cybersecurity investment priorities",
    ],
  },
};

export default function Onboarding({ onComplete, theme, onToggleTheme }) {
  const [step, setStep] = useState(1); // 1=dept, 2=role, 3=summary
  const [department, setDepartment] = useState(null);
  const [role, setRole] = useState(null);

  const deptData = department ? DEPARTMENTS[department] : null;

  const handleDeptSelect = (dept) => {
    setDepartment(dept);
    setRole(null);
    setStep(2);
  };

  const handleRoleSelect = (r) => {
    setRole(r);
    setStep(3);
  };

  const handleStart = () => {
    onComplete({ department, role });
  };

  return (
    <div className="onboarding-overlay">
      <button
        className="theme-toggle onboarding-theme-toggle"
        onClick={onToggleTheme}
        title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
      >
        <span className="theme-icon">{theme === "dark" ? "Light" : "Dark"}</span>
      </button>
      <div className="onboarding-card">
        <div className="onboarding-header">
          <img className="onboarding-logo" src="/company-logo.png" alt="C&S Logo" />
          <h1>Fiona</h1>
          <p className="onboarding-sub">
            C&S Cybersecurity Assistant — let's personalize your experience.
          </p>
        </div>

        {/* Step indicator */}
        <div className="step-indicator">
          <span className={`step-dot ${step >= 1 ? "active" : ""}`}>1</span>
          <span className="step-line" />
          <span className={`step-dot ${step >= 2 ? "active" : ""}`}>2</span>
          <span className="step-line" />
          <span className={`step-dot ${step >= 3 ? "active" : ""}`}>3</span>
        </div>

        {/* Step 1: Department */}
        {step === 1 && (
          <div className="onboarding-step">
            <h2>Which department do you work in?</h2>
            <div className="dept-grid">
              {Object.entries(DEPARTMENTS).map(([name, info]) => (
                <button
                  key={name}
                  className={`dept-btn ${department === name ? "selected" : ""}`}
                  onClick={() => handleDeptSelect(name)}
                >
                  <span className="dept-icon">{info.icon}</span>
                  <span className="dept-name">{name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Role */}
        {step === 2 && deptData && (
          <div className="onboarding-step">
            <h2>
              {department} — Select your role
            </h2>
            <div className="role-grid">
              {deptData.roles.map((r) => (
                <button
                  key={r}
                  className={`role-btn ${role === r ? "selected" : ""}`}
                  onClick={() => handleRoleSelect(r)}
                >
                  {r}
                </button>
              ))}
            </div>
            <button className="back-link" onClick={() => setStep(1)}>
              ← Change department
            </button>
          </div>
        )}

        {/* Step 3: Summary */}
        {step === 3 && deptData && (
          <div className="onboarding-step">
            <h2>
              How Fiona helps {department}
            </h2>
            <p className="persona-desc">{deptData.description}</p>

            <div className="persona-badge">
              {department} · {role}
            </div>

            <h3>What I can help you with:</h3>
            <ul className="use-cases">
              {deptData.useCases.map((uc, i) => (
                <li key={i}>{uc}</li>
              ))}
            </ul>

            <button className="start-btn" onClick={handleStart}>
              Get Started
            </button>
            <button className="back-link" onClick={() => setStep(2)}>
              ← Change role
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
