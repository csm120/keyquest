import { useState } from "react";

export default function App() {
  const [count, setCount] = useState(0);

  return (
    <main style={{ maxWidth: 720, margin: "4rem auto", padding: "0 1rem", lineHeight: 1.5 }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>KeyQuest</h1>
      <p style={{ marginBottom: "1rem" }}>
        A fast, accessible typing game. Press “Start” to begin a 30-second round.
      </p>

      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", margin: "1rem 0" }}>
        <button
          onClick={() => setCount((c) => c + 1)}
          style={{ padding: "0.6rem 1rem", fontSize: "1rem", cursor: "pointer" }}
          aria-label="Start round"
        >
          Start
        </button>
        <span aria-live="polite">count is {count}</span>
      </div>

      <p style={{ color: "#555" }}>
        (Placeholder UI—logos and template hints removed. We’ll wire the real game next.)
      </p>
    </main>
  );
}
