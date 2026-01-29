import React, { useEffect, useRef } from "react";

function renderBoldMarkdown(text) {
  const raw = String(text ?? "");
  if (!raw.includes("**")) return raw;

  // Safely render **bold** without using innerHTML.
  const parts = [];
  const re = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let m;
  while ((m = re.exec(raw)) !== null) {
    const start = m.index;
    const end = re.lastIndex;
    if (start > lastIndex) parts.push(raw.slice(lastIndex, start));
    parts.push(<strong key={`b-${start}-${end}`}>{m[1]}</strong>);
    lastIndex = end;
  }
  if (lastIndex < raw.length) parts.push(raw.slice(lastIndex));
  return parts;
}

export default function ChatWindow({ messages = [], isTyping = false, onSendSuggestion }) {
  const chatContainer = useRef(null);

  useEffect(() => {
    if (!chatContainer.current) return;
    chatContainer.current.scrollTop = chatContainer.current.scrollHeight;
  }, [messages.length, isTyping]);

  return (
    <div className="chat-window" ref={chatContainer}>
      {messages.length === 0 && (
        <div className="welcome">
          <h2>Welcome</h2>
          <p>
            Your cybersecurity assistant for incident response, threat analysis, and security best
            practices.
          </p>

          <div className="suggestions">
            <button
              className="suggestion-chip"
              onClick={() => onSendSuggestion?.("How do I triage a suspicious email?")}
              type="button"
            >
              Triage Phishing Email
            </button>
            <button
              className="suggestion-chip"
              onClick={() => onSendSuggestion?.("Summarize best practices for MFA rollout")}
              type="button"
            >
              MFA Best Practices
            </button>
            <button
              className="suggestion-chip"
              onClick={() => onSendSuggestion?.("What should be in an incident response plan?")}
              type="button"
            >
              Incident Response
            </button>
            <button
              className="suggestion-chip"
              onClick={() => onSendSuggestion?.("How to secure AWS S3 buckets?")}
              type="button"
            >
              Cloud Security
            </button>
          </div>
        </div>
      )}

      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.type}`}>
          <div>{renderBoldMarkdown(msg.text)}</div>
          {msg.timestamp && <div className="timestamp">{msg.timestamp}</div>}
        </div>
      ))}

      {isTyping && (
        <div className="message bot">
          <div className="typing" aria-label="Assistant typing">
            <span />
            <span />
            <span />
          </div>
        </div>
      )}
    </div>
  );
}

