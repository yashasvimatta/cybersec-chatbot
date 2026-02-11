import React, { useState, useRef, useEffect } from "react";

function FionaHeaderAvatar() {
  return (
    <svg width="36" height="36" viewBox="0 0 40 40" fill="none" className="header-fiona-avatar">
      <circle cx="20" cy="20" r="20" fill="var(--fiona-accent, #a6e22e)" />
      <circle cx="20" cy="16" r="8" fill="var(--fiona-face, #272822)" />
      <ellipse cx="20" cy="34" rx="12" ry="9" fill="var(--fiona-face, #272822)" />
      <circle cx="17" cy="15" r="1.5" fill="var(--fiona-accent, #a6e22e)" />
      <circle cx="23" cy="15" r="1.5" fill="var(--fiona-accent, #a6e22e)" />
      <path d="M17 19 Q20 22 23 19" stroke="var(--fiona-accent, #a6e22e)" strokeWidth="1.2" fill="none" strokeLinecap="round" />
    </svg>
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
            <span className="tools-item-icon">&#128680;</span>
            <div className="tools-item-text">
              <strong>Report Incident</strong>
              <span>Phishing, suspicious activity, data leak — email the Cybersecurity Team</span>
            </div>
          </button>

          <button
            className="tools-item"
            onClick={() => { onOpenChecklists(); setOpen(false); }}
          >
            <span className="tools-item-icon">&#9745;</span>
            <div className="tools-item-text">
              <strong>My Security Tasks</strong>
              <span>Interactive checklists — new employee setup, access reviews, remote work security</span>
            </div>
          </button>

          {isAdmin && (
            <button
              className="tools-item"
              onClick={() => { onOpenAnalytics(); setOpen(false); }}
            >
              <span className="tools-item-icon">&#128202;</span>
              <div className="tools-item-text">
                <strong>Analytics Dashboard</strong>
                <span>Query volume, satisfaction scores, knowledge gaps, department usage</span>
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
            <span className="tools-item-icon">&#127760;</span>
            <div className="tools-item-text">
              <strong>Cybersecurity Website</strong>
              <span>Policies, training materials, and self-service resources</span>
            </div>
          </a>

          <a
            className="tools-item"
            href="mailto:CyberSecurity@cswg.com"
            onClick={() => setOpen(false)}
          >
            <span className="tools-item-icon">&#9993;</span>
            <div className="tools-item-text">
              <strong>Email Cybersecurity Team</strong>
              <span>CyberSecurity@cswg.com &middot; Helpdesk: 603-354-7500</span>
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
  onSwitchPersona,
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
          <span className="theme-icon">{theme === "dark" ? "\u2600\uFE0F" : "\uD83C\uDF19"}</span>
        </button>

        <ToolsMenu
          persona={persona}
          onReportIncident={onReportIncident}
          onOpenChecklists={onOpenChecklists}
          onOpenAnalytics={onOpenAnalytics}
        />

        {onSwitchPersona && (
          <button className="btn btn-outline" onClick={onSwitchPersona} title="Change department/role">
            Switch Role
          </button>
        )}

        <button className="btn btn-danger" onClick={onReset}>
          Reset Chat
        </button>
      </div>
    </header>
  );
}
