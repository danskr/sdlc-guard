import React, {FormEvent, useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

type Finding = {
  finding_type: string;
  severity: string;
  title: string;
  description: string;
  artifacts: string[];
  recommendation: string;
};

type Evidence = {
  artifact_id: string;
  artifact_type: string;
  title: string;
  excerpt: string;
  source: string;
  score: number | null;
};

type QueryResponse = {
  question: string;
  analysis_type: string;
  answer: string;
  findings: Finding[];
  evidence: Evidence[];
  ragflow_used: boolean;
};

type Message =
  | {
      id: number;
      role: "user";
      text: string;
    }
  | {
      id: number;
      role: "assistant";
      text: string;
      result: QueryResponse;
    };

const prompts = [
  "Is checkout ready for release?",
  "Do you see any inconsistencies in the current scope of the project?",
  "Are there any approved functionalities not covered by test implementation?",
  "Are there any functionalities that are not implemented at all and have no source code counterpart?",
  "Is there source code that has no approved requirement?",
  "Which non-functional requirements have not been verified?"
];

function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, c => c.toUpperCase());
}

function ResultView({result}: {result: QueryResponse}) {
  const [tab, setTab] =
    useState<"analysis" | "findings" | "evidence">("analysis");

  const high =
    result.findings.filter(f => f.severity.toLowerCase() === "high").length;

  const medium =
    result.findings.filter(f => f.severity.toLowerCase() === "medium").length;

  return (
    <div className="result">
      <div className="result-meta">
        <span className="badge analysis-type">
          {humanize(result.analysis_type)}
        </span>

        {high > 0 && (
          <span className="badge high">
            {high} high
          </span>
        )}

        {medium > 0 && (
          <span className="badge medium">
            {medium} medium
          </span>
        )}

        <span
          className={
            result.ragflow_used
              ? "badge rag-active"
              : "badge rag-inactive"
          }
        >
          RAGFlow {result.ragflow_used ? "active" : "not used"}
        </span>
      </div>

      <div className="tabs">
        <button
          className={tab === "analysis" ? "active" : ""}
          onClick={() => setTab("analysis")}
        >
          Analysis
        </button>

        <button
          className={tab === "findings" ? "active" : ""}
          onClick={() => setTab("findings")}
        >
          Findings ({result.findings.length})
        </button>

        <button
          className={tab === "evidence" ? "active" : ""}
          onClick={() => setTab("evidence")}
        >
          Evidence ({result.evidence.length})
        </button>
      </div>

      {tab === "analysis" && (
        <div className="analysis-text">
          {result.answer}
        </div>
      )}

      {tab === "findings" && (
        <div className="finding-list">
          {result.findings.length === 0 ? (
            <div className="empty">
              No deterministic findings were returned.
            </div>
          ) : (
            result.findings.map((finding, index) => (
              <div className="finding-card" key={index}>
                <div className="finding-header">
                  <span
                    className={`severity ${finding.severity.toLowerCase()}`}
                  >
                    {finding.severity}
                  </span>

                  <strong>{finding.title}</strong>
                </div>

                <p>{finding.description}</p>

                {finding.artifacts.length > 0 && (
                  <div className="artifact-row">
                    {finding.artifacts.map(artifact => (
                      <code key={artifact}>{artifact}</code>
                    ))}
                  </div>
                )}

                <div className="recommendation">
                  <strong>Recommendation</strong>
                  <p>{finding.recommendation}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {tab === "evidence" && (
        <div className="evidence-list">
          {result.evidence.length === 0 ? (
            <div className="empty">
              No evidence was returned.
            </div>
          ) : (
            result.evidence.map((evidence, index) => (
              <div className="evidence-card" key={index}>
                <div className="evidence-header">
                  <div>
                    <strong>{evidence.artifact_id}</strong>
                    <div className="evidence-title">
                      {evidence.title}
                    </div>
                  </div>

                  <div className="evidence-badges">
                    <span
                      className={
                        evidence.source === "ragflow"
                          ? "source rag"
                          : "source trace"
                      }
                    >
                      {evidence.source}
                    </span>

                    {evidence.score !== null && (
                      <span className="score">
                        {evidence.score.toFixed(3)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="artifact-type">
                  {humanize(evidence.artifact_type)}
                </div>

                <pre>{evidence.excerpt}</pre>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [nextId, setNextId] = useState(1);
  const [error, setError] = useState<string | null>(null);

  async function ask(text: string) {
    const trimmed = text.trim();

    if (!trimmed || loading) {
      return;
    }

    const userId = nextId;
    const assistantId = nextId + 1;

    setNextId(nextId + 2);
    setQuestion("");
    setError(null);

    setMessages(previous => [
      ...previous,
      {
        id: userId,
        role: "user",
        text: trimmed
      }
    ]);

    setLoading(true);

    try {
      const response = await fetch("/api/v1/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          question: trimmed
        })
      });

      if (!response.ok) {
        throw new Error(
          `SDLC-Guard returned HTTP ${response.status}`
        );
      }

      const result: QueryResponse = await response.json();

      setMessages(previous => [
        ...previous,
        {
          id: assistantId,
          role: "assistant",
          text: result.answer,
          result
        }
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to contact SDLC-Guard."
      );
    } finally {
      setLoading(false);
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void ask(question);
  }

  return (
    <div className="app-shell">
      <header>
        <div className="brand">
          <div className="logo">
            SG
          </div>

          <div>
            <h1>SDLC-Guard</h1>
            <p>
              AI-assisted scope, traceability and release analysis
            </p>
          </div>
        </div>

        <div className="status">
          <span className="status-dot" />
          Connected
        </div>
      </header>

      <main>
        {messages.length === 0 && (
          <section className="welcome">
            <div className="welcome-icon">◇</div>

            <h2>Ask SDLC-Guard about the project</h2>

            <p>
              Analyze requirements, source code, tests,
              traceability, inconsistencies and release readiness.
            </p>

            <div className="prompt-grid">
              {prompts.map(prompt => (
                <button
                  key={prompt}
                  onClick={() => void ask(prompt)}
                >
                  <span>{prompt}</span>
                  <span className="arrow">→</span>
                </button>
              ))}
            </div>
          </section>
        )}

        <section className="conversation">
          {messages.map(message => {
            if (message.role === "user") {
              return (
                <div className="message user-message" key={message.id}>
                  <div className="message-label">You</div>
                  <div className="bubble user-bubble">
                    {message.text}
                  </div>
                </div>
              );
            }

            return (
              <div
                className="message assistant-message"
                key={message.id}
              >
                <div className="message-label">
                  <span className="small-logo">SG</span>
                  SDLC-Guard
                </div>

                <div className="bubble assistant-bubble">
                  <ResultView result={message.result} />
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="message assistant-message">
              <div className="message-label">
                <span className="small-logo">SG</span>
                SDLC-Guard
              </div>

              <div className="bubble assistant-bubble thinking">
                <span />
                <span />
                <span />
                Analyzing project evidence...
              </div>
            </div>
          )}

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </section>
      </main>

      <footer>
        <form onSubmit={submit}>
          <textarea
            value={question}
            onChange={event => setQuestion(event.target.value)}
            placeholder="Ask SDLC-Guard about scope, implementation, tests or release readiness..."
            rows={2}
            disabled={loading}
            onKeyDown={event => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                void ask(question);
              }
            }}
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
          >
            Ask
          </button>
        </form>

        <div className="footer-note">
          Answers combine deterministic traceability analysis
          with semantic RAGFlow evidence.
        </div>
      </footer>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
