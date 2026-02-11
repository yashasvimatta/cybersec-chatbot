import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

export default function SecurityChecklist({ onClose, persona }) {
  const [checklists, setChecklists] = useState([]);
  const [active, setActive] = useState(null);
  const [checked, setChecked] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get(`${API_BASE}/checklists`, {
          params: { department: persona?.department },
        });
        setChecklists(res.data.checklists || []);
      } catch {
        setChecklists([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [persona?.department]);

  // Load checked state from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("fiona-checklists");
      if (saved) setChecked(JSON.parse(saved));
    } catch {}
  }, []);

  const toggleItem = (checklistId, idx) => {
    setChecked((prev) => {
      const key = `${checklistId}_${idx}`;
      const next = { ...prev, [key]: !prev[key] };
      try { localStorage.setItem("fiona-checklists", JSON.stringify(next)); } catch {}
      return next;
    });
  };

  const getProgress = (checklist) => {
    let done = 0;
    checklist.items.forEach((_, i) => {
      if (checked[`${checklist.id}_${i}`]) done++;
    });
    return done;
  };

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-card" onClick={(e) => e.stopPropagation()}>
          <p style={{ textAlign: "center", padding: 40 }}>Loading checklists...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{active ? active.title : "Security Checklists"}</h2>
          <button className="modal-close" onClick={active ? () => setActive(null) : onClose}>
            {active ? "\u2190" : "\u00D7"}
          </button>
        </div>

        {!active ? (
          <div className="checklist-grid">
            {checklists.map((cl) => {
              const done = getProgress(cl);
              const pct = Math.round((done / cl.total) * 100);
              return (
                <button key={cl.id} className="checklist-card" onClick={() => setActive(cl)}>
                  <div className="checklist-card-title">{cl.title}</div>
                  <div className="checklist-card-desc">{cl.description}</div>
                  <div className="checklist-progress">
                    <div className="checklist-progress-bar">
                      <div className="checklist-progress-fill" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="checklist-progress-text">{done}/{cl.total}</span>
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="checklist-items">
            <p className="checklist-desc">{active.description}</p>
            {active.items.map((item, i) => {
              const key = `${active.id}_${i}`;
              const isDone = !!checked[key];
              return (
                <label key={i} className={`checklist-item ${isDone ? "done" : ""}`}>
                  <input
                    type="checkbox"
                    checked={isDone}
                    onChange={() => toggleItem(active.id, i)}
                  />
                  <span className="checklist-item-text">{item}</span>
                </label>
              );
            })}
            <div className="checklist-summary">
              {getProgress(active)} of {active.total} completed
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
