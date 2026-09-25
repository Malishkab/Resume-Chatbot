import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const CANDIDATE_NAME = "Malishka Bhardwaj";
const STARTER_QUESTIONS = [
  "Walk me through your most recent role.",
  "What are your strongest technical skills?",
  "Tell me about a project you're proud of.",
];

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        `I'm standing in for ${CANDIDATE_NAME} here. Ask me anything you'd ask in an interview — about their experience, skills, or projects.`,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const threadEndRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  async function sendQuestion(question) {
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
    } catch (err) {
      setError(
        "Couldn't reach the server. Check that the backend is running and reachable."
      );
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    sendQuestion(input);
  }

  const hasChatted = messages.length > 1;

  return (
    <div className="page">
      <header className="masthead">
        <div className="masthead-inner">
          <span className="eyebrow">Interview mode</span>
          <h1>{CANDIDATE_NAME}</h1>
          <p className="tagline">Answering as the candidate, from their resume.</p>
        </div>
      </header>

      <main className="thread" aria-live="polite">
        <div className="thread-inner">
          {messages.map((m, i) => (
            <div key={i} className={`bubble-row ${m.role}`}>
              <div className="bubble">{m.content}</div>
            </div>
          ))}

          {isLoading && (
            <div className="bubble-row assistant">
              <div className="bubble bubble-loading">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}

          <div ref={threadEndRef} />
        </div>
      </main>

      {!hasChatted && (
        <div className="starters">
          {STARTER_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              className="starter-chip"
              onClick={() => sendQuestion(q)}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <form className="composer" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question, HR-style..."
          disabled={isLoading}
          aria-label="Your question"
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;