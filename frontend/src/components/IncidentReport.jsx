import React, { useState } from "react";

const INCIDENT_TYPES = [
  { id: "phishing", label: "Phishing / Suspicious Email", icon: "🎣" },
  { id: "suspicious_activity", label: "Suspicious Activity", icon: "👁" },
  { id: "data_leak", label: "Data Leak / Exposure", icon: "💧" },
  { id: "lost_device", label: "Lost / Stolen Device", icon: "📱" },
  { id: "malware", label: "Malware / Ransomware", icon: "🦠" },
  { id: "unauthorized_access", label: "Unauthorized Access", icon: "🔓" },
  { id: "other", label: "Other", icon: "📋" },
];

const URGENCY_LEVELS = [
  { id: "low", label: "Low", desc: "No immediate impact" },
  { id: "medium", label: "Medium", desc: "Potential impact if not addressed" },
  { id: "high", label: "High", desc: "Active threat or data exposure" },
  { id: "critical", label: "Critical", desc: "Ongoing breach or system compromise" },
];

export default function IncidentReport({ onClose, onSubmit, persona }) {
  const [incidentType, setIncidentType] = useState(null);
  const [description, setDescription] = useState("");
  const [urgency, setUrgency] = useState("medium");
  const [senderEmail, setSenderEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async () => {
    if (!incidentType || !description.trim() || !senderEmail.trim()) return;
    setSubmitting(true);
    try {
      const res = await onSubmit({ incidentType, description, urgency, senderEmail });
      setResult(res);
      // Auto-open the email client
      if (res.mailto_url) {
        window.location.href = res.mailto_url;
      }
    } catch {
      setResult({ error: true });
    } finally {
      setSubmitting(false);
    }
  };

  if (result) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-card" onClick={(e) => e.stopPropagation()}>
          <div className="incident-result">
            {result.error ? (
              <>
                <div className="result-icon">!</div>
                <h2>Submission Failed</h2>
                <p>Please try again or contact the Cybersecurity Team directly at <strong>CyberSecurity@cswg.com</strong></p>
              </>
            ) : (
              <>
                <div className="result-icon result-success">&#10003;</div>
                <h2>Incident Reported</h2>
                <p className="result-ref">Reference: <strong>{result.reference}</strong></p>
                <p>Your email client should have opened with the report pre-filled. Just hit <strong>Send</strong> to deliver it to <strong>CyberSecurity@cswg.com</strong>.</p>
                <p className="incident-persona-note">If your email client didn't open, click below:</p>
                <a
                  href={result.mailto_url}
                  className="start-btn"
                  style={{ display: "block", textAlign: "center", textDecoration: "none", marginBottom: 8 }}
                >
                  Open Email to CyberSecurity@cswg.com
                </a>
              </>
            )}
            <button className="btn btn-outline" onClick={onClose} style={{ width: "100%", marginTop: 8 }}>Close</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Report a Security Incident</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="incident-form">
          <label className="form-label">Your Email</label>
          <input
            className="incident-email-input"
            type="email"
            placeholder="your.name@cswg.com"
            value={senderEmail}
            onChange={(e) => setSenderEmail(e.target.value)}
          />

          <label className="form-label">What type of incident?</label>
          <div className="incident-type-grid">
            {INCIDENT_TYPES.map((t) => (
              <button
                key={t.id}
                className={`incident-type-btn ${incidentType === t.id ? "selected" : ""}`}
                onClick={() => setIncidentType(t.id)}
              >
                <span className="incident-type-icon">{t.icon}</span>
                <span>{t.label}</span>
              </button>
            ))}
          </div>

          <label className="form-label">Urgency</label>
          <div className="urgency-row">
            {URGENCY_LEVELS.map((u) => (
              <button
                key={u.id}
                className={`urgency-btn urgency-${u.id} ${urgency === u.id ? "selected" : ""}`}
                onClick={() => setUrgency(u.id)}
                title={u.desc}
              >
                {u.label}
              </button>
            ))}
          </div>

          <label className="form-label">Describe what happened</label>
          <textarea
            className="incident-textarea"
            rows={4}
            placeholder="Include details: what you saw, when it happened, any affected systems or people..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <div className="incident-meta-row">
            {persona && (
              <span className="incident-persona-note">
                Reporting as: {persona.department} / {persona.role}
              </span>
            )}
            <span className="incident-persona-note">
              Sent to: CyberSecurity@cswg.com
            </span>
          </div>

          <button
            className="start-btn"
            onClick={handleSubmit}
            disabled={!incidentType || !description.trim() || !senderEmail.trim() || submitting}
          >
            {submitting ? "Submitting..." : "Submit & Send Email"}
          </button>
        </div>
      </div>
    </div>
  );
}
