import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

// Fallback icons in case API is slow
const BU_ICONS = {
  "Supply Chain": "🚛",
  "Commercial": "💼",
  "HR": "👥",
  "Legal": "⚖️",
  "IS/IT": "🛡️",
  "Finance": "💰",
  "Procurement": "📦",
  "Retail": "🛒",
};

export default function Sidebar({ persona, onPersonaChange, collapsed, onToggleCollapse }) {
  const [expandedDept, setExpandedDept] = useState(persona?.department || null);
  const [buData, setBuData] = useState({});

  // Load archetypes from backend on mount
  useEffect(() => {
    axios.get(`${API_BASE}/personas`)
      .then((res) => setBuData(res.data))
      .catch(() => {}); // fail silently — sidebar still renders with icons
  }, []);

  const handleDeptClick = (dept) => {
    setExpandedDept(expandedDept === dept ? null : dept);
  };

  const handleRoleClick = (dept, archetype) => {
    onPersonaChange({ department: dept, role: archetype.name, archetypeId: archetype.id });
  };

  const departments = Object.keys(buData).length > 0 ? Object.keys(buData) : Object.keys(BU_ICONS);

  return (
    <aside className={`sidebar ${collapsed ? "sidebar-collapsed" : ""}`}>
      <div className="sidebar-header">
        <img className="sidebar-logo" src="/company-logo.png" alt="C&S Logo" />
        {!collapsed && (
          <div className="sidebar-brand">
            <div className="sidebar-title">Fiona</div>
            <div className="sidebar-subtitle">Cybersecurity Assistant</div>
          </div>
        )}
        <button
          className="sidebar-collapse-btn"
          onClick={onToggleCollapse}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? "\u276F" : "\u276E"}
        </button>
      </div>

      {!collapsed && (
        <div className="sidebar-label">Department</div>
      )}

      <nav className="sidebar-nav">
        {departments.map((name) => {
          const icon = buData[name]?.icon || BU_ICONS[name] || "🏢";
          const archetypes = buData[name]?.archetypes || [];
          const isActive = persona?.department === name;
          const isExpanded = expandedDept === name;

          return (
            <div key={name} className="sidebar-dept-group">
              <button
                className={`sidebar-dept-btn ${isActive ? "active" : ""} ${isExpanded ? "expanded" : ""}`}
                onClick={() => handleDeptClick(name)}
                title={collapsed ? name : undefined}
              >
                <span className="sidebar-dept-icon">{icon}</span>
                {!collapsed && (
                  <>
                    <span className="sidebar-dept-name">{name}</span>
                    <span className={`sidebar-chevron ${isExpanded ? "open" : ""}`}>&#9662;</span>
                  </>
                )}
              </button>

              {isExpanded && !collapsed && (
                <div className="sidebar-roles">
                  {archetypes.map((a) => (
                    <button
                      key={a.id}
                      className={`sidebar-role-btn ${persona?.department === name && persona?.role === a.name ? "active" : ""}`}
                      onClick={() => handleRoleClick(name, a)}
                      title={a.description}
                    >
                      {a.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {!collapsed && persona && (
        <div className="sidebar-persona">
          <div className="sidebar-persona-label">Active Role</div>
          <div className="sidebar-persona-badge">
            {BU_ICONS[persona.department] || "🏢"} {persona.department} &middot; {persona.role}
          </div>
        </div>
      )}
    </aside>
  );
}
