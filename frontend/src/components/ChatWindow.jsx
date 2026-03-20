import React, { useEffect, useRef, useState } from "react";

/* ── Archetype-specific starter questions (3 per role) ─── */

const ARCHETYPE_QUESTIONS = {
  // Supply Chain
  "Warehouse Floor Worker": [
    "What should I do if I find a suspicious USB device in the warehouse?",
    "Who do I contact if my handheld scanner starts behaving strangely?",
    "What are the rules for using my personal phone on the warehouse floor?",
  ],
  "Warehouse Supervisor / Manager": [
    "How do I remove system access when a team member leaves?",
    "What is our procedure if a warehouse system goes offline unexpectedly?",
    "How do I brief my team after a new phishing threat is identified?",
  ],
  "Transportation & Logistics": [
    "What security checks apply when connecting to a customer or supplier network?",
    "How do I handle sensitive delivery documentation securely?",
    "What do I do if my vehicle tracking system is behaving unexpectedly?",
  ],
  "Supply Chain Director / VP": [
    "What is our supplier cybersecurity assessment process?",
    "Summarise our business continuity plan for a cyber incident",
    "What controls govern third-party vendor access to our systems?",
  ],

  // Commercial
  "Sales Representative": [
    "How do I share a proposal securely with an external client?",
    "What CRM data can I access on a personal device?",
    "I received an unusual payment request from a client — what should I do?",
  ],
  "Merchandising & Category": [
    "How do I share product data securely with suppliers?",
    "What are the rules for accessing supplier portals?",
    "How do I protect commercially sensitive pricing data?",
  ],
  "Customer Experience & Service": [
    "How should I handle a customer who shares personal data over chat?",
    "What do I do if a customer account shows signs of suspicious activity?",
    "What customer data am I permitted to share over the phone?",
  ],
  "Commercial Leadership": [
    "What are our data protection obligations for customer data?",
    "Summarise our email security policy for external communications",
    "What is our incident response plan for a customer data breach?",
  ],

  // HR
  "HR Business Partner / Recruiter": [
    "How do I share candidate CVs securely with hiring managers?",
    "What personal data can I store in our applicant tracking system?",
    "How do I handle a data subject access request from a candidate?",
  ],
  "HR Operations & Benefits": [
    "How do I protect employee payroll data?",
    "What are the rules for storing employee medical information?",
    "How do I securely provision system access for a new starter?",
  ],
  "HR Leadership": [
    "What are our obligations if employee personal data is breached?",
    "Summarise our joiner-mover-leaver access control policy",
    "How do we track security awareness training completion?",
  ],

  // Legal
  "Compliance & Regulatory": [
    "What are our breach notification timelines under GDPR?",
    "How do we document our data processing activities?",
    "Which compliance frameworks apply to our operations?",
  ],
  "Attorney / Legal Counsel": [
    "How do I share legally privileged documents securely?",
    "What encryption standards apply to confidential legal files?",
    "How do I manage a legal hold on employee data?",
  ],
  "Legal & Risk Leadership": [
    "Summarise our current regulatory compliance posture",
    "What cyber risks belong on our board risk register?",
    "What is our legal exposure in a ransomware incident?",
  ],

  // IS/IT
  "IT Support & Security Operations": [
    "Walk me through our incident response process for a confirmed phishing attempt",
    "How do I revoke system access for a terminated employee?",
    "What is our procedure for a suspected malware infection?",
  ],
  "Engineer / Developer": [
    "What are our secure coding standards?",
    "How should I handle secrets and API keys in our codebase?",
    "What is our patch management policy and SLA?",
  ],
  "Architect / Senior Engineer": [
    "What are our cloud security architecture principles?",
    "How do we enforce network segmentation across environments?",
    "Summarise our zero-trust implementation approach",
  ],
  "IS/IT Leadership": [
    "What are our cybersecurity KPIs for 2026?",
    "Summarise the key findings from our latest penetration test",
    "What does our current threat landscape look like?",
  ],

  // Finance
  "Accounts Payable / Receivable": [
    "How do I verify a new supplier bank account to avoid payment fraud?",
    "What do I do if I receive an unexpected invoice from a known supplier?",
    "How do I report a suspected payment fraud attempt?",
  ],
  "Financial Analyst / Accountant": [
    "How do I share financial reports securely with external auditors?",
    "What data classification applies to our financial models?",
    "What are the access controls for our finance systems?",
  ],
  "Finance Manager / Director": [
    "What controls prevent unauthorised access to our financial systems?",
    "How do we detect and respond to financial fraud?",
    "What is our policy on finance system access for employees who have left?",
  ],
  "Finance Leadership": [
    "What is our exposure to financial cyber fraud?",
    "Summarise our PCI-DSS compliance status",
    "What controls govern access to our treasury systems?",
  ],

  // Procurement
  "Buyer / Merchandiser": [
    "How do I assess a new supplier's cybersecurity posture?",
    "What security clauses should I look for in a supplier contract?",
    "How do I share tender documents securely?",
  ],
  "Demand Planning & Inventory": [
    "How do I protect demand forecast data shared with suppliers?",
    "What access do third parties have to our inventory systems?",
    "How do I report a data incident involving a supplier?",
  ],
  "Procurement Manager": [
    "What is our vendor risk assessment process?",
    "How do we monitor third-party access to our systems?",
    "What are our minimum cybersecurity requirements for suppliers?",
  ],
  "Procurement Leadership": [
    "Summarise our supply chain cyber risk exposure",
    "What is our process for offboarding a high-risk supplier?",
    "How do we verify supplier compliance with our security standards?",
  ],

  // Retail
  "Store Operations": [
    "What do I do if a payment terminal behaves unexpectedly?",
    "How do I report a suspected card skimmer on a till?",
    "What are the rules for using personal devices in-store?",
  ],
  "Retail Merchandising & Marketing": [
    "How do I share campaign assets securely with external agencies?",
    "What customer data can we lawfully use for marketing?",
    "How do I protect commercially sensitive promotional plans?",
  ],
  "Retail Leadership": [
    "What is our incident response plan for a store system outage?",
    "Summarise our PCI-DSS compliance status for retail",
    "What cyber risks are specific to our retail estate?",
  ],
};

/* ── Markdown renderer ─────────────────────────────────── */

function renderMarkdown(text) {
  const raw = String(text ?? "");
  if (!raw) return null;
  const lines = raw.split("\n");
  const elements = [];
  let key = 0;
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim().startsWith("```")) {
      const lang = line.trim().slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++;
      elements.push(
        <pre key={key++} className="md-code-block">
          {lang && <span className="md-code-lang">{lang}</span>}
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
      continue;
    }

    if (/^-{3,}$/.test(line.trim()) || /^\*{3,}$/.test(line.trim())) {
      elements.push(<hr key={key++} className="md-hr" />);
      i++;
      continue;
    }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const Tag = `h${Math.min(level + 1, 6)}`;
      elements.push(
        <Tag key={key++} className={`md-heading md-h${level}`}>
          {renderInline(headingMatch[2])}
        </Tag>
      );
      i++;
      continue;
    }

    if (/^\s*[-*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
        i++;
      }
      elements.push(
        <ul key={key++} className="md-list">
          {items.map((item, j) => (
            <li key={j}>{renderInline(item)}</li>
          ))}
        </ul>
      );
      continue;
    }

    if (/^\s*\d+[.)]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+[.)]\s+/, ""));
        i++;
      }
      elements.push(
        <ol key={key++} className="md-list md-ol">
          {items.map((item, j) => (
            <li key={j}>{renderInline(item)}</li>
          ))}
        </ol>
      );
      continue;
    }

    if (line.trim() === "") {
      elements.push(<div key={key++} className="md-spacer" />);
      i++;
      continue;
    }

    elements.push(
      <p key={key++} className="md-para">
        {renderInline(line)}
      </p>
    );
    i++;
  }

  return elements;
}

function renderInline(text) {
  const raw = String(text ?? "");
  const re = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)/g;
  const parts = [];
  let lastIndex = 0;
  let m;
  let k = 0;

  while ((m = re.exec(raw)) !== null) {
    if (m.index > lastIndex) parts.push(raw.slice(lastIndex, m.index));
    const matched = m[0];
    if (matched.startsWith("`")) {
      parts.push(<code key={`c-${k++}`} className="md-inline-code">{matched.slice(1, -1)}</code>);
    } else if (matched.startsWith("**")) {
      parts.push(<strong key={`b-${k++}`} className="md-bold">{matched.slice(2, -2)}</strong>);
    } else if (matched.startsWith("*")) {
      parts.push(<em key={`i-${k++}`} className="md-italic">{matched.slice(1, -1)}</em>);
    }
    lastIndex = re.lastIndex;
  }
  if (lastIndex < raw.length) parts.push(raw.slice(lastIndex));
  return parts.length === 1 && typeof parts[0] === "string" ? parts[0] : parts;
}

/* ── Avatars ───────────────────────────────────────────── */

function FionaAvatar({ size = 32 }) {
  return (
    <div
      className="avatar avatar-fiona"
      style={{ width: size, height: size, fontSize: size * 0.4, lineHeight: `${size}px` }}
    >
      F
    </div>
  );
}

function UserAvatar({ persona, size = 32 }) {
  const initial = persona?.role ? persona.role.charAt(0).toUpperCase() : "U";
  return (
    <div className="avatar avatar-user" style={{ width: size, height: size, fontSize: size * 0.45 }}>
      {initial}
    </div>
  );
}

/* ── Message action buttons ────────────────────────────── */

function MessageActions({ msg, onFeedback, onEscalate, onSendSuggestion }) {
  const [feedbackGiven, setFeedbackGiven] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleFeedback = (rating) => {
    setFeedbackGiven(rating);
    onFeedback?.(msg, rating);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(msg.text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="msg-actions">
      <button
        className={`msg-action-btn ${feedbackGiven === "up" ? "active-up" : ""}`}
        onClick={() => handleFeedback("up")}
        disabled={feedbackGiven !== null}
        title="Helpful"
      >
        &#128077;
      </button>
      <button
        className={`msg-action-btn ${feedbackGiven === "down" ? "active-down" : ""}`}
        onClick={() => handleFeedback("down")}
        disabled={feedbackGiven !== null}
        title="Not helpful"
      >
        &#128078;
      </button>

      <button className="msg-action-btn" onClick={handleCopy} title="Copy answer">
        {copied ? "\u2713" : "\u2398"}
      </button>

      {feedbackGiven === "down" && (
        <button
          className="msg-action-btn escalate-btn"
          onClick={() => onEscalate?.(msg)}
          title="Escalate to Cybersecurity Team"
        >
          Ask a Human
        </button>
      )}

      {msg.followUps?.length > 0 && (
        <div className="follow-ups">
          {msg.followUps.map((q, i) => (
            <button
              key={i}
              className="follow-up-chip"
              onClick={() => onSendSuggestion?.(q)}
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Confidence badge ──────────────────────────────────── */

function ConfidenceBadge({ confidence }) {
  if (confidence == null || confidence === undefined) return null;
  const pct = Math.round(confidence * 100);
  let label, cls;
  if (pct >= 70) { label = "High confidence"; cls = "conf-high"; }
  else if (pct >= 40) { label = "Moderate confidence"; cls = "conf-med"; }
  else { label = "General knowledge"; cls = "conf-low"; }
  return <span className={`confidence-badge ${cls}`}>{label}</span>;
}

/* ── Tip Card ──────────────────────────────────────────── */

function TipCard({ tip, onDismiss }) {
  if (!tip) return null;
  return (
    <div className="tip-card">
      <div className="tip-card-header">
        <span className="tip-card-label">Tip of the Day</span>
        <button className="tip-card-dismiss" onClick={onDismiss}>&times;</button>
      </div>
      <div className="tip-card-body md-content">{renderMarkdown(tip.tip)}</div>
    </div>
  );
}

/* ── Welcome screen ────────────────────────────────────── */

function WelcomeScreen({ persona, tip, onDismissTip, onSendSuggestion, onReportIncident, onOpenChecklists }) {
  const questions = ARCHETYPE_QUESTIONS[persona.role] || [];

  return (
    <div className="welcome">
      <TipCard tip={tip} onDismiss={onDismissTip} />

      <div className="welcome-avatar">
        <FionaAvatar size={64} />
      </div>

      <h2 className="welcome-title">Hi, I am Fiona</h2>
      <p className="welcome-subtitle">
        Your cybersecurity assistant, configured for{" "}
        <strong>{persona.role}</strong> in {persona.department}.
      </p>

      {questions.length > 0 && (
        <div className="welcome-starters">
          <p className="welcome-starters-label">Suggested questions for your role</p>
          <div className="starter-list">
            {questions.map((q, i) => (
              <button
                key={i}
                className="starter-item"
                onClick={() => onSendSuggestion?.(q)}
                type="button"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="welcome-actions">
        <button className="welcome-action-btn" onClick={onReportIncident} type="button">
          Report an Incident
        </button>
        <button className="welcome-action-btn" onClick={onOpenChecklists} type="button">
          Security Checklists
        </button>
      </div>
    </div>
  );
}

/* ── Main Component ────────────────────────────────────── */

export default function ChatWindow({
  messages = [],
  isTyping = false,
  onSendSuggestion,
  persona,
  onFeedback,
  onEscalate,
  tip,
  onDismissTip,
  onReportIncident,
  onOpenChecklists,
}) {
  const chatContainer = useRef(null);

  useEffect(() => {
    if (!chatContainer.current) return;
    chatContainer.current.scrollTop = chatContainer.current.scrollHeight;
  }, [messages.length, isTyping]);

  return (
    <div className="chat-window" ref={chatContainer}>
      {messages.length === 0 && (
        <WelcomeScreen
          persona={persona}
          tip={tip}
          onDismissTip={onDismissTip}
          onSendSuggestion={onSendSuggestion}
          onReportIncident={onReportIncident}
          onOpenChecklists={onOpenChecklists}
        />
      )}

      {messages.map((msg) => (
        <div key={msg.id} className={`msg-row ${msg.type}`}>
          <div className="msg-avatar">
            {msg.type === "bot" ? (
              <FionaAvatar size={30} />
            ) : msg.type === "user" ? (
              <UserAvatar persona={persona} size={30} />
            ) : null}
          </div>
          <div className={`message ${msg.type}`}>
            {msg.type === "bot" && (
              <div className="msg-meta-top">
                <span className="msg-sender">Fiona</span>
                <ConfidenceBadge confidence={msg.confidence} />
              </div>
            )}
            <div className="md-content">{renderMarkdown(msg.text)}</div>
            {msg.type === "bot" && msg.sources?.length > 0 && (
              <div className="msg-sources">
                <span className="msg-sources-label">Sources</span>
                <div className="msg-sources-list">
                  {msg.sources.map((s, i) => (
                    <span key={i} className="msg-source-tag">{s.name || s.source_name}</span>
                  ))}
                </div>
              </div>
            )}
            {msg.timestamp && <div className="timestamp">{msg.timestamp}</div>}
            {msg.type === "bot" && (
              <MessageActions
                msg={msg}
                onFeedback={onFeedback}
                onEscalate={onEscalate}
                onSendSuggestion={onSendSuggestion}
              />
            )}
          </div>
        </div>
      ))}

      {isTyping && (
        <div className="msg-row bot">
          <div className="msg-avatar"><FionaAvatar size={30} /></div>
          <div className="message bot">
            <div className="typing" aria-label="Assistant typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
