import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

function StatCard({ label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

function BarChart({ data, labelKey, valueKey, maxBars = 8 }) {
  const items = data.slice(0, maxBars);
  const maxVal = Math.max(...items.map((d) => d[valueKey]), 1);
  return (
    <div className="bar-chart">
      {items.map((d, i) => (
        <div key={i} className="bar-row">
          <div className="bar-label">{d[labelKey]}</div>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{ width: `${(d[valueKey] / maxVal) * 100}%` }}
            />
          </div>
          <div className="bar-value">{d[valueKey]}</div>
        </div>
      ))}
    </div>
  );
}

export default function AnalyticsDashboard({ onClose }) {
  const [summary, setSummary] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sumRes, gapRes] = await Promise.all([
          axios.get(`${API_BASE}/analytics/summary?days=30`),
          axios.get(`${API_BASE}/analytics/gaps?limit=15`),
        ]);
        setSummary(sumRes.data);
        setGaps(gapRes.data.gaps || []);
      } catch (err) {
        console.error("Analytics load error:", err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-card" onClick={(e) => e.stopPropagation()}>
          <p style={{ textAlign: "center", padding: 40 }}>Loading analytics...</p>
        </div>
      </div>
    );
  }

  const fb = summary?.feedback || {};

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card modal-xl" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analytics Dashboard</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="analytics-content">
          {/* Top-level stats */}
          <div className="stats-row">
            <StatCard label="Total Queries (30d)" value={summary?.total_queries || 0} />
            <StatCard
              label="Satisfaction"
              value={`${fb.satisfaction_pct || 0}%`}
              sub={`${fb.up || 0} up / ${fb.down || 0} down`}
            />
            <StatCard
              label="Feedback Total"
              value={fb.total || 0}
            />
          </div>

          {/* Department breakdown */}
          {summary?.by_department?.length > 0 && (
            <div className="analytics-section">
              <h3>Queries by Department</h3>
              <BarChart data={summary.by_department} labelKey="department" valueKey="cnt" />
            </div>
          )}

          {/* Daily volume */}
          {summary?.daily_volume?.length > 0 && (
            <div className="analytics-section">
              <h3>Daily Volume</h3>
              <BarChart data={summary.daily_volume} labelKey="day" valueKey="cnt" maxBars={14} />
            </div>
          )}

          {/* KB Gaps */}
          {gaps.length > 0 && (
            <div className="analytics-section">
              <h3>Knowledge Base Gaps</h3>
              <p className="analytics-desc">
                Queries with low confidence or negative feedback — topics to add to the KB.
              </p>
              <div className="gaps-list">
                {gaps.map((g, i) => (
                  <div key={i} className="gap-item">
                    <span className={`gap-badge gap-${g.reason === "negative_feedback" ? "feedback" : "confidence"}`}>
                      {g.reason === "negative_feedback" ? "Thumbs Down" : "Low Confidence"}
                    </span>
                    <span className="gap-query">{g.query}</span>
                    {g.department && <span className="gap-dept">{g.department}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Low confidence queries */}
          {summary?.low_confidence_queries?.length > 0 && (
            <div className="analytics-section">
              <h3>Low Confidence Answers</h3>
              <div className="gaps-list">
                {summary.low_confidence_queries.map((q, i) => (
                  <div key={i} className="gap-item">
                    <span className="gap-badge gap-confidence">
                      {Math.round((q.confidence || 0) * 100)}%
                    </span>
                    <span className="gap-query">{q.query}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
