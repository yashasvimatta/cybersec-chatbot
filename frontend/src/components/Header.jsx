import React from "react";

export default function Header({ status = "Connected", onReset }) {
  return (
    <header className="app-header">
      <div className="header-left">
        <img className="brand-logo" src="/company-logo.png" alt="Company logo" />
        <div className="brand-text">
          <div className="title">Fiona</div>
          <div className="subtitle">Cybersecurity Assistant</div>
        </div>
      </div>

      <div className="header-right">
        <div className="status">
          <span className="status-dot" />
          <span>{status}</span>
        </div>
        <button className="btn btn-danger" onClick={onReset}>
          Reset Chat
        </button>
      </div>
    </header>
  );
}

