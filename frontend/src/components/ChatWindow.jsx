import React, { useEffect, useRef, useState } from "react";

/** Common security questions -- shown for every department */
const COMMON_SECURITY_QUESTIONS = [
  "How do I securely share files with others?",
  "How should I encrypt sensitive emails?",
  "What's the acceptable use policy for internet browsing?",
  "A message got blocked -- who do I contact?",
  "I got a suspicious email -- what should I do?",
  "What can I do to help keep us cyber secure?",
];

const PERSONA_SUGGESTIONS = {
  Finance: [
    "What are our data protection policies for financial systems?",
    "How should we handle a suspicious transaction or fraud attempt?",
    "What access controls should finance team members follow?",
    "Summarize PCI-DSS compliance requirements relevant to us",
  ],
  "Supply Chain": [
    "What are the security requirements for third-party vendor access?",
    "How do we protect warehouse and logistics systems?",
    "What's our business continuity plan for cyber incidents?",
    "Summarize our network security policy",
  ],
  IS: [
    "What are our incident response procedures?",
    "Show me the latest vulnerability assessment findings",
    "What firewall rules are pending removal?",
    "What are our KPIs for 2026?",
  ],
  Retail: [
    "What security measures protect our POS systems?",
    "How do I report a suspected security incident at a store?",
    "What are best practices for workstation security?",
    "Summarize our security awareness training policy",
  ],
  Commercial: [
    "What's our data classification policy for commercial documents?",
    "How should we securely share files with external partners?",
    "What are our email security policies?",
    "How do we protect customer data in our CRM?",
  ],
  Procurement: [
    "How do we assess vendor cybersecurity risk?",
    "What security clauses should be in vendor contracts?",
    "What access management policies apply to procurement tools?",
    "Summarize our asset management policy",
  ],
  Legal: [
    "What are our data breach notification obligations?",
    "Summarize the IS Security Policy",
    "What compliance frameworks do we follow?",
    "What are the legal implications of a security incident?",
  ],
  HR: [
    "What's the process for revoking access when an employee leaves?",
    "Summarize our security awareness training policy",
    "How do we protect employee PII and HR data?",
    "What's our workstation security policy for remote workers?",
  ],
  ELT: [
    "Give me an executive summary of our security posture",
    "What are our cybersecurity KPIs for 2026?",
    "Summarize the top risks from recent pen test findings",
    "What's our incident response readiness level?",
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
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" className="avatar avatar-fiona">
      <circle cx="20" cy="20" r="20" fill="var(--fiona-accent, #a6e22e)" />
      <circle cx="20" cy="16" r="8" fill="var(--fiona-face, #272822)" />
      <ellipse cx="20" cy="34" rx="12" ry="9" fill="var(--fiona-face, #272822)" />
      <circle cx="17" cy="15" r="1.5" fill="var(--fiona-accent, #a6e22e)" />
      <circle cx="23" cy="15" r="1.5" fill="var(--fiona-accent, #a6e22e)" />
      <path d="M17 19 Q20 22 23 19" stroke="var(--fiona-accent, #a6e22e)" strokeWidth="1.2" fill="none" strokeLinecap="round" />
      <circle cx="20" cy="20" r="19.5" stroke="var(--fiona-accent, #a6e22e)" strokeWidth="1" fill="none" opacity="0.3" />
    </svg>
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
      {/* Feedback */}
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

      {/* Copy */}
      <button className="msg-action-btn" onClick={handleCopy} title="Copy answer">
        {copied ? "\u2713" : "\u2398"}
      </button>

      {/* Escalate (only on thumbs down) */}
      {feedbackGiven === "down" && (
        <button
          className="msg-action-btn escalate-btn"
          onClick={() => onEscalate?.(msg)}
          title="Escalate to Cybersecurity Team"
        >
          Ask a Human
        </button>
      )}

      {/* Follow-ups */}
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
  popularQuestions,
}) {
  const chatContainer = useRef(null);

  useEffect(() => {
    if (!chatContainer.current) return;
    chatContainer.current.scrollTop = chatContainer.current.scrollHeight;
  }, [messages.length, isTyping]);

  const deptSuggestions = persona?.department
    ? PERSONA_SUGGESTIONS[persona.department] || []
    : [];

  return (
    <div className="chat-window" ref={chatContainer}>
      {messages.length === 0 && (
        <div className="welcome">
          {/* Tip of the day */}
          <TipCard tip={tip} onDismiss={onDismissTip} />

          <div className="welcome-avatar">
            <FionaAvatar size={72} />
          </div>
          <h2>
            {persona
              ? `Hi! I'm Fiona, your ${persona.department} assistant.`
              : "Welcome"}
          </h2>
          <p>
            {persona
              ? `Tailored for ${persona.role} in ${persona.department}. Ask me anything about security policies, threats, compliance, or our internal knowledge base.`
              : "Your cybersecurity assistant for incident response, threat analysis, and security best practices."}
          </p>

          {deptSuggestions.length > 0 && (
            <>
              <h4 className="suggestions-label">{persona.department} Questions</h4>
              <div className="suggestions">
                {deptSuggestions.map((s, i) => (
                  <button
                    key={`dept-${i}`}
                    className="suggestion-chip"
                    onClick={() => onSendSuggestion?.(s)}
                    type="button"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </>
          )}

          <h4 className="suggestions-label">Common Security Questions</h4>
          <div className="suggestions">
            {COMMON_SECURITY_QUESTIONS.map((s, i) => (
              <button
                key={`common-${i}`}
                className="suggestion-chip suggestion-chip-common"
                onClick={() => onSendSuggestion?.(s)}
                type="button"
              >
                {s}
              </button>
            ))}
          </div>

          {/* Popular questions from real usage */}
          {popularQuestions?.length > 0 && (
            <>
              <h4 className="suggestions-label">Trending in Your Department</h4>
              <div className="suggestions">
                {popularQuestions.map((q, i) => (
                  <button
                    key={`pop-${i}`}
                    className="suggestion-chip suggestion-chip-popular"
                    onClick={() => onSendSuggestion?.(q.query)}
                    type="button"
                  >
                    {q.query}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
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
            <div className="md-content">{renderMarkdown(msg.text)}</div>
            {msg.type === "bot" && <ConfidenceBadge confidence={msg.confidence} />}
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
