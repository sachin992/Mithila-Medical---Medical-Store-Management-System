import React from "react";
import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function AssistantPage() {
  const { token, user } = useAuth();
  const [threads, setThreads] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [threadId, setThreadId] = useState("");
  const [question, setQuestion] = useState("What was total revenue last month?");
  const [mode, setMode] = useState("readonly");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  async function loadMemory(selectedThreadId) {
    if (!selectedThreadId) {
      setChatHistory([]);
      return;
    }
    try {
      const memory = await apiRequest(`/assistant/threads/${selectedThreadId}/memory`, { token });
      setChatHistory(
        memory.map((m) => ({
          role: m.role === "admin" ? "admin" : "bot",
          text: m.content,
          created_at: m.created_at,
        }))
      );
    } catch (err) {
      setStatus(err.message);
    }
  }

  useEffect(() => {
    if (user?.role === "admin") {
      Promise.all([
        apiRequest("/assistant/threads", { token }),
        apiRequest("/assistant/templates", { token }),
      ])
        .then(([t, temp]) => {
          setThreads(t);
          setTemplates(temp);
          if (t[0]) {
            setThreadId(String(t[0].id));
            loadMemory(t[0].id);
          }
        })
        .catch((err) => setStatus(err.message));
    }
  }, [token, user]);

  useEffect(() => {
    loadMemory(threadId);
  }, [threadId]);

  if (user?.role !== "admin") return <p>Admin access only.</p>;

  async function createThread() {
    try {
      const t = await apiRequest("/assistant/threads", {
        method: "POST",
        token,
        body: { title: "Admin Analytics", mode, retention_days: 30 },
      });
      setThreads([t, ...threads]);
      setThreadId(String(t.id));
      setChatHistory([]);
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function runQuery() {
    try {
      const data = await apiRequest("/assistant/query", {
        method: "POST",
        token,
        body: {
          thread_id: Number(threadId),
          message: question,
          mode,
          confirm_write: false,
        },
      });
      setResult(data);
      setStatus(data.summary);
      await loadMemory(threadId);
      if (data.rows?.length) {
        setChatHistory((prev) => [...prev, { role: "bot", text: "Result rows", rows: data.rows }]);
      }
    } catch (err) {
      setStatus(err.message);
    }
  }

  return (
    <section className="dual-grid">
      <div className="panel">
        <h2>Admin Analytics Chat</h2>
        <p>Ask stock, revenue, and selling questions in natural language.</p>
        <div className="inline-row">
          <select value={threadId} onChange={(e) => setThreadId(e.target.value)}>
            <option value="">Select thread</option>
            {threads.map((t) => (
              <option key={t.id} value={t.id}>{t.title} ({t.mode})</option>
            ))}
          </select>
          <button className="ghost-btn" onClick={createThread}>New Chat Thread</button>
        </div>
        <select value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="readonly">Read-only analytics</option>
        </select>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={5}
          placeholder="Ask: What was revenue in last year? Show top selling medicines..."
        />
        <button className="primary-btn" onClick={runQuery}>Ask Analytics Bot</button>
        {status ? <p>{status}</p> : null}
      </div>
      <div className="panel">
        <h2>Saved Analytics Questions</h2>
        <ul>
          {templates.map((t) => (
            <li key={t.key}>
              <strong>{t.title}</strong>
              <button className="ghost-btn" onClick={() => setQuestion(t.prompt)}>Use</button>
            </li>
          ))}
        </ul>
        <h3>Chat</h3>
        <div>
          {chatHistory.map((item, idx) => (
            <div key={idx}>
              <p><strong>{item.role === "admin" ? "Admin" : "Bot"}:</strong> {item.text}</p>
              {item.rows && item.rows.length ? <pre>{JSON.stringify(item.rows, null, 2)}</pre> : null}
            </div>
          ))}
        </div>
        <h3>Latest Structured Response</h3>
        <pre>{result ? JSON.stringify(result, null, 2) : "No result yet"}</pre>
      </div>
    </section>
  );
}
