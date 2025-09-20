import { useEffect, useRef, useState } from "react";
import SkipLink from "./components/SkipLink";
import LiveRegion from "./components/LiveRegion";
import { useCountdown } from "./hooks/useCountdown";

export default function App() {
  const [announcement, setAnnouncement] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const playAgainRef = useRef<HTMLButtonElement>(null);

  const { timeLeft, running, start, pause, reset } = useCountdown({
    durationSec: 30,
    onAnnounce: setAnnouncement
  });

  // Focus handling: on start -> input; on time’s up -> play again
  useEffect(() => {
    if (running && inputRef.current) inputRef.current.focus();
  }, [running]);

  useEffect(() => {
    if (!running && timeLeft === 0 && playAgainRef.current) {
      playAgainRef.current.focus();
    }
  }, [running, timeLeft]);

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === "Space") { e.preventDefault(); running ? pause() : start(); }
      if (e.code === "Escape") { e.preventDefault(); reset(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [running, start, pause, reset]);

  return (
    <main style={{ maxWidth: 720, margin: "2rem auto", padding: "0 1rem", lineHeight: 1.5 }}>
      <SkipLink targetId="main" />
      <LiveRegion message={announcement} />

      <header>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>KeyQuest</h1>
        <p>Press <kbd>Space</kbd> to Start/Pause, <kbd>Esc</kbd> to Reset.</p>
      </header>

      <section id="main" aria-label="Typing round">
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", margin: "1rem 0" }}>
          <button onClick={() => (running ? pause() : start())} aria-pressed={running}>
            {running ? "Pause" : "Start"}
          </button>
          <button onClick={reset}>Reset</button>
          <span aria-live="off" aria-label={`Time left ${timeLeft} seconds`}>
            {timeLeft}s
          </span>
        </div>

        <label htmlFor="typing" style={{ display: "block", marginBottom: 8 }}>
          Type here:
        </label>
        <input
          id="typing"
          ref={inputRef}
          type="text"
          style={{ width: "100%", padding: 8, fontSize: 16 }}
          placeholder="Start a round, then type…"
        />

        {!running && timeLeft === 0 && (
          <div style={{ marginTop: 16 }}>
            <p role="status">Time’s up! Great job. Want to play again?</p>
            <button ref={playAgainRef} onClick={() => { reset(); start(); }}>
              Play again
            </button>
          </div>
        )}
      </section>
    </main>
  );
}
