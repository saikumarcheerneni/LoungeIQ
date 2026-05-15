import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const API = "http://localhost:8000";

function statusColor(pct) {
  if (pct < 40) return "#22c55e";
  if (pct < 70) return "#f59e0b";
  if (pct < 90) return "#f97316";
  return "#ef4444";
}

function statusLabel(pct) {
  if (pct < 40) return "Quiet";
  if (pct < 70) return "Moderate";
  if (pct < 90) return "Busy";
  return "Full";
}

function LoungeCard({ lounge }) {
  const color = statusColor(lounge.occupancy_pct);
  return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, border: `2px solid ${color}`, flex: 1, minWidth: 180 }}>
      <div style={{ fontSize: 12, color: "#94a3b8" }}>{lounge.lounge_id}</div>
      <div style={{ fontSize: 15, fontWeight: 700, color: "#f1f5f9", margin: "4px 0 12px" }}>{lounge.name}</div>
      <div style={{ fontSize: 34, fontWeight: 800, color }}>{lounge.occupancy_pct}%</div>
      <div style={{ display: "inline-block", background: color + "22", color, borderRadius: 6, padding: "2px 10px", fontSize: 12, fontWeight: 600, margin: "6px 0 10px" }}>
        {statusLabel(lounge.occupancy_pct)}
      </div>
      <div style={{ fontSize: 12, color: "#94a3b8" }}>Terminal {lounge.terminal} · {lounge.available_spots} spots free</div>
      <div style={{ marginTop: 10, background: "#334155", borderRadius: 4, height: 7 }}>
        <div style={{ width: `${lounge.occupancy_pct}%`, background: color, borderRadius: 4, height: 7, transition: "width 0.5s" }} />
      </div>
    </div>
  );
}

function Chatbot() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I'm the LoungeIQ Assistant ✈ Tell me your ticket class, loyalty tier, and gate — I'll find the best lounge for you!" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: userMsg }) });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", text: data.reply || "Sorry, I could not process that." }]);
    } catch {
      setMessages(prev => [...prev, { role: "assistant", text: "⚠️ Make sure FastAPI is running on localhost:8000" }]);
    }
    setLoading(false);
  }

  return (
    <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, display: "flex", flexDirection: "column", height: 400 }}>
      <div style={{ fontSize: 15, fontWeight: 700, color: "#f1f5f9", marginBottom: 12 }}>✈ LoungeIQ Assistant</div>
      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8, marginBottom: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ alignSelf: m.role === "user" ? "flex-end" : "flex-start", background: m.role === "user" ? "#3b82f6" : "#334155", color: "#f1f5f9", borderRadius: 10, padding: "8px 14px", maxWidth: "80%", fontSize: 13 }}>
            {m.text}
          </div>
        ))}
        {loading && <div style={{ color: "#64748b", fontSize: 12 }}>Thinking...</div>}
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()}
          placeholder="e.g. Business class from gate B12..."
          style={{ flex: 1, background: "#334155", border: "none", borderRadius: 8, padding: "9px 12px", color: "#f1f5f9", fontSize: 13, outline: "none" }} />
        <button onClick={send} style={{ background: "#3b82f6", color: "white", border: "none", borderRadius: 8, padding: "9px 16px", cursor: "pointer", fontWeight: 600 }}>Send</button>
      </div>
    </div>
  );
}

export default function App() {
  const [lounges, setLounges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  async function fetchStatus() {
    try {
      const res = await fetch(`${API}/status`);
      const data = await res.json();
      setLounges(data.lounges || []);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch { }
    setLoading(false);
  }

  useEffect(() => { fetchStatus(); const t = setInterval(fetchStatus, 30000); return () => clearInterval(t); }, []);

  const avg = lounges.length ? Math.round(lounges.reduce((s, l) => s + l.occupancy_pct, 0) / lounges.length) : 0;
  const full = lounges.filter(l => l.occupancy_pct >= 90).length;

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#f1f5f9", fontFamily: "Inter, system-ui, sans-serif", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 24, fontWeight: 800 }}>✈ LoungeIQ Dashboard</h1>
          <div style={{ color: "#64748b", fontSize: 12, marginTop: 3 }}>Airport Lounge Intelligence Platform</div>
        </div>
        <div style={{ fontSize: 12, color: "#64748b" }}>Updated: {lastUpdated || "—"}</div>
      </div>

      <div style={{ display: "flex", gap: 14, marginBottom: 24 }}>
        {[{ label: "Total Lounges", value: lounges.length, color: "#3b82f6" },
          { label: "Avg Occupancy", value: `${avg}%`, color: avg > 70 ? "#f97316" : "#22c55e" },
          { label: "At Capacity", value: full, color: full > 0 ? "#ef4444" : "#22c55e" }
        ].map(s => (
          <div key={s.label} style={{ background: "#1e293b", borderRadius: 10, padding: "14px 20px", flex: 1 }}>
            <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>{s.label}</div>
            <div style={{ fontSize: 26, fontWeight: 800, color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 24 }}>
        {loading ? <div style={{ color: "#64748b" }}>Loading...</div> : lounges.map(l => <LoungeCard key={l.lounge_id} lounge={l} />)}
      </div>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 20, flex: 2, minWidth: 280 }}>
          <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 14 }}>Occupancy Overview</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={lounges}>
              <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 8 }} formatter={v => [`${v}%`, "Occupancy"]} />
              <Bar dataKey="occupancy_pct" radius={[4, 4, 0, 0]}>
                {lounges.map((l, i) => <Cell key={i} fill={statusColor(l.occupancy_pct)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{ flex: 1, minWidth: 280 }}><Chatbot /></div>
      </div>
    </div>
  );
}