import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

export default function NewsletterSubscribe({ onClose, persona }) {
  const [email, setEmail]     = useState("");
  const [status, setStatus]   = useState("idle"); // idle | loading | success | error
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = email.trim().toLowerCase();
    if (!trimmed || !trimmed.includes("@")) {
      setStatus("error");
      setMessage("Please enter a valid email address.");
      return;
    }

    setStatus("loading");
    try {
      const res = await axios.post(`${API_BASE}/subscribe`, {
        email: trimmed,
        department: persona?.department || null,
        role: persona?.role || null,
      });
      setStatus("success");
      setMessage(res.data.message || "You're subscribed!");
    } catch (err) {
      setStatus("error");
      setMessage(
        err.response?.data?.detail ||
        "Subscription failed. Please try again."
      );
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="modal-card"
        style={{ maxWidth: 440, width: "100%", padding: "0" }}
      >
        {/* Header */}
        <div
          style={{
            background: "var(--bg-tertiary)",
            borderBottom: "1px solid var(--border)",
            padding: "20px 24px 16px",
            borderRadius: "12px 12px 0 0",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: "50%",
              background: "var(--accent-green)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 18,
              flexShrink: 0,
            }}
          >
            📬
          </div>
          <div style={{ flex: 1 }}>
            <div
              style={{
                fontWeight: 700,
                fontSize: 16,
                color: "var(--text-primary)",
              }}
            >
              Fiona Weekly Newsletter
            </div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 2 }}>
              From the C&S Cybersecurity Team
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--text-muted)",
              fontSize: 20,
              cursor: "pointer",
              lineHeight: 1,
              padding: "0 4px",
            }}
          >
            ×
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: "24px" }}>
          {status === "success" ? (
            <div style={{ textAlign: "center", padding: "16px 0" }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎉</div>
              <div
                style={{
                  fontSize: 16,
                  fontWeight: 600,
                  color: "var(--accent-green)",
                  marginBottom: 8,
                }}
              >
                You're subscribed!
              </div>
              <div
                style={{
                  fontSize: 14,
                  color: "var(--text-secondary)",
                  lineHeight: 1.6,
                }}
              >
                {message}
                <br />
                Every week you'll get security tips, top questions, and
                insights from your Fiona usage.
              </div>
              <button
                onClick={onClose}
                className="btn"
                style={{
                  marginTop: 20,
                  background: "var(--accent-green)",
                  color: "#111",
                  border: "none",
                  padding: "10px 28px",
                  borderRadius: 8,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Got it
              </button>
            </div>
          ) : (
            <>
              {/* What you'll get */}
              <div style={{ marginBottom: 20 }}>
                <div
                  style={{
                    fontSize: 13,
                    color: "var(--text-secondary)",
                    lineHeight: 1.7,
                    marginBottom: 14,
                  }}
                >
                  Get a curated weekly digest straight to your inbox —
                  delivered every Monday morning.
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 8,
                  }}
                >
                  {[
                    ["🔒", "Security tip of the week"],
                    ["📊", "Usage stats & top questions"],
                    ["💡", "Cybersecurity reminders"],
                    ["🔍", "Knowledge gaps to watch"],
                  ].map(([icon, label]) => (
                    <div
                      key={label}
                      style={{
                        background: "var(--bg-tertiary)",
                        border: "1px solid var(--border)",
                        borderRadius: 8,
                        padding: "10px 12px",
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                      }}
                    >
                      <span style={{ fontSize: 16 }}>{icon}</span>
                      <span
                        style={{
                          fontSize: 12,
                          color: "var(--text-secondary)",
                          lineHeight: 1.4,
                        }}
                      >
                        {label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit}>
                <label
                  style={{
                    display: "block",
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--text-muted)",
                    marginBottom: 6,
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                  }}
                >
                  Work Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (status === "error") setStatus("idle");
                  }}
                  placeholder="you@cswg.com"
                  autoFocus
                  style={{
                    width: "100%",
                    padding: "11px 14px",
                    background: "var(--bg-input)",
                    border: `1px solid ${status === "error" ? "var(--accent-pink)" : "var(--border)"}`,
                    borderRadius: 8,
                    color: "var(--text-primary)",
                    fontSize: 14,
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />

                {status === "error" && (
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--accent-pink)",
                      marginTop: 6,
                    }}
                  >
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={status === "loading"}
                  style={{
                    width: "100%",
                    marginTop: 14,
                    padding: "12px",
                    background:
                      status === "loading"
                        ? "var(--bg-tertiary)"
                        : "var(--accent-green)",
                    color: status === "loading" ? "var(--text-muted)" : "#0f1117",
                    border: "none",
                    borderRadius: 8,
                    fontWeight: 700,
                    fontSize: 14,
                    cursor: status === "loading" ? "not-allowed" : "pointer",
                    transition: "background 0.2s",
                  }}
                >
                  {status === "loading" ? "Subscribing…" : "Subscribe to Newsletter"}
                </button>
              </form>

              <div
                style={{
                  marginTop: 12,
                  fontSize: 11,
                  color: "var(--text-muted)",
                  textAlign: "center",
                  lineHeight: 1.5,
                }}
              >
                Weekly on Mondays · Unsubscribe anytime · No spam
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
