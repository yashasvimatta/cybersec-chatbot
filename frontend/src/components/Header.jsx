import React, { useState, useRef, useEffect } from "react";

function FionaHeaderAvatar() {
  return (
    <div className="avatar avatar-fiona header-fiona-avatar" style={{ width: 34, height: 34, fontSize: 14, lineHeight: "34px" }}>
      F
    </div>
  );
}

function ToolsMenu({ persona, onReportIncident, onOpenChecklists, onOpenAnalytics }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    if (open) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const isAdmin = persona?.department === "IS" || persona?.department === "ELT";

  return (
    <div className="tools-menu-wrap" ref={ref}>
      <button className="btn btn-tools" onClick={() => setOpen(!open)}>
        <span className="tools-icon">&#9776;</span> Tools
      </button>

      {open && (
        <div className="tools-dropdown">
          <button
            className="tools-item"
            onClick={() => { onReportIncident(); setOpen(false); }}
          >
            <div className="tools-item-text">
              <strong>Report Incident</strong>
              <span>Phishing, suspicious activity, data leak</span>
            </div>
          </button>

          <button
            className="tools-item"
            onClick={() => { onOpenChecklists(); setOpen(false); }}
          >
            <div className="tools-item-text">
              <strong>Security Tasks</strong>
              <span>Checklists for setup, access reviews, remote work</span>
            </div>
          </button>

          {isAdmin && (
            <button
              className="tools-item"
              onClick={() => { onOpenAnalytics(); setOpen(false); }}
            >
              <div className="tools-item-text">
                <strong>Analytics</strong>
                <span>Query volume, satisfaction, knowledge gaps</span>
              </div>
            </button>
          )}

          <a
            className="tools-item"
            href="https://sites.google.com/cswg.com/cybersecurity"
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => setOpen(false)}
          >
            <div className="tools-item-text">
              <strong>Cybersecurity Website</strong>
              <span>Policies, training, and resources</span>
            </div>
          </a>

          <a
            className="tools-item"
            href="mailto:CyberSecurity@cswg.com"
            onClick={() => setOpen(false)}
          >
            <div className="tools-item-text">
              <strong>Contact Cybersecurity Team</strong>
              <span>CyberSecurity@cswg.com &middot; 603-354-7500</span>
            </div>
          </a>
        </div>
      )}
    </div>
  );
}

export default function Header({
  status = "Connected",
  onReset,
  persona,
  theme,
  onToggleTheme,
  onReportIncident,
  onOpenChecklists,
  onOpenAnalytics,
}) {
  return (
    <header className="app-header">
      <div className="header-left">
        <FionaHeaderAvatar />
        <div className="brand-text">
          <div className="title">Fiona</div>
          <div className="subtitle">
            {persona
              ? `${persona.department} \u00B7 ${persona.role}`
              : "Cybersecurity Assistant"}
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className="status">
          <span className="status-dot" />
          <span>{status}</span>
        </div>

        <button
          className="theme-toggle"
          onClick={onToggleTheme}
          title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          <span className="theme-icon">{theme === "dark" ? "Light" : "Dark"}</span>
        </button>

        <ToolsMenu
          persona={persona}
          onReportIncident={onReportIncident}
          onOpenChecklists={onOpenChecklists}
          onOpenAnalytics={onOpenAnalytics}
        />

        <button className="btn btn-danger" onClick={onReset}>
          Reset Chat
        </button>
      </div>
    </header>
  );
}
