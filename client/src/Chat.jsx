import { useState } from "react";

function Chat() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.response },
      ]);
    } catch (err) {
      console.error("Chat failed:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error — could not reach the server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Ask about events</h2>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "16px",
          minHeight: "200px",
          marginBottom: "12px",
          backgroundColor: "#fafafa",
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: "#888" }}>
            Try: "What's free this weekend?" or "Any concerts this week?"
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: "12px" }}>
            <strong>{msg.role === "user" ? "You" : "OnLo"}:</strong>{" "}
            <span style={{ whiteSpace: "pre-wrap" }}>{msg.text}</span>
          </div>
        ))}
        {loading && <p style={{ color: "#888" }}>Thinking...</p>}
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          style={{
            flex: 1,
            padding: "8px",
            borderRadius: "4px",
            border: "1px solid #ccc",
          }}
          disabled={loading}
        />
        <button onClick={sendQuestion} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
