import { useEffect, useRef, useState } from "react";

/**
 * KeyQuest — Tutorial-gated Adventure (TypeScript) + Adaptive Difficulty
 * Adapts to recent accuracy and reaction time (no Easy/Hard menu).
 * Sounds toggle included. Hints & penalties on.
 */

type Phase = "idle" | "tutorial" | "adventure" | "summary";
type Target = { code: " " | "ArrowLeft" | "ArrowRight" | "ArrowUp" | "ArrowDown"; label: string };
type Prompt = { text: string; expect: Array<Target["code"]>; hint?: string };

const TARGET_TIMES = 3;
const TARGETS: Target[] = [
  { code: " ", label: "Space" },
  { code: "ArrowLeft", label: "Left Arrow" },
  { code: "ArrowRight", label: "Right Arrow" },
  { code: "ArrowUp", label: "Up Arrow" },
  { code: "ArrowDown", label: "Down Arrow" },
];

const ARROW_SET = new Set<Target["code"]>(["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"]);
const WASD_SET = new Set<string>(["w", "a", "s", "d", "W", "A", "S", "D"]);

// Base timings (ms)
const BASE_HINT_DELAY_MS = 6500;
const BASE_PROMPT_IDLE_TIMEOUT_MS = 5500;
const PROMPT_COOLDOWN_MS = 250;

const PROMPTS: Prompt[] = [
  { text: "Press Space!", expect: [" "], hint: "Space is the long bar at the bottom center." },
  { text: "Tap Left!", expect: ["ArrowLeft"], hint: "Arrow cluster is bottom-right; Left is on the left." },
  { text: "Tap Right!", expect: ["ArrowRight"], hint: "Arrow cluster is bottom-right; Right is on the right." },
  { text: "Go Up!", expect: ["ArrowUp"], hint: "In the inverted T cluster, Up sits above Left and Right." },
  { text: "Go Down!", expect: ["ArrowDown"], hint: "Down is below Up, between Left and Right." },
  { text: "Obstacle ahead: Jump over it!", expect: ["ArrowUp"], hint: "Use Up Arrow to jump." },
  { text: "Low doorway: Duck!", expect: ["ArrowDown"], hint: "Use Down Arrow to duck." },
  { text: "Path splits: Move left!", expect: ["ArrowLeft"], hint: "Left Arrow to take the left path." },
  { text: "Path splits: Move right!", expect: ["ArrowRight"], hint: "Right Arrow to take the right path." },
  { text: "Collect the token: Hit Space!", expect: [" "], hint: "Hit Space to collect." },
];

// --- Web Audio (simple tones) ---
function makeAudio() {
  const Ctx = (window as any).AudioContext || (window as any).webkitAudioContext;
  if (!Ctx) return null;
  return new Ctx();
}
function playTone(ctx: AudioContext, freq: number, durationMs = 120, type: OscillatorType = "sine") {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.value = 0.12;
  osc.connect(gain).connect(ctx.destination);
  osc.start();
  setTimeout(() => { try { osc.stop(); } catch {} }, durationMs);
}

export default function App(): JSX.Element {
  // ---------- Global & Tutorial State ----------
  const [phase, setPhase] = useState<Phase>("idle");
  const [message, setMessage] = useState<string>("Welcome to KeyQuest. Press Start to begin the free tutorial.");
  const [counts, setCounts] = useState<Record<Target["code"], number>>({
    " ": 0, ArrowLeft: 0, ArrowRight: 0, ArrowUp: 0, ArrowDown: 0,
  });
  const [current, setCurrent] = useState<Target | null>(null);
  const [started, setStarted] = useState<boolean>(false);
  const [canBeginAdventure, setCanBeginAdventure] = useState<boolean>(false);

  // ---------- Adventure State ----------
  const [score, setScore] = useState<number>(0);
  const [correct, setCorrect] = useState<number>(0);
  const [wrong, setWrong] = useState<number>(0);
  const [streak, setStreak] = useState<number>(0);
  const [bestStreak, setBestStreak] = useState<number>(0);
  const [adventurePrompt, setAdventurePrompt] = useState<Prompt | null>(null);
  const [adventureTimeLeft, setAdventureTimeLeft] = useState<number | null>(null); // hidden

  // ---------- Adaptive Skill Tracking ----------
  type Sample = { rt: number; ok: boolean };
  const [recent, setRecent] = useState<Sample[]>([]);
  const promptShownAtRef = useRef<number | null>(null);

  const skillScore = (() => {
    if (recent.length === 0) return 0; // start gentle
    const acc = recent.filter(s => s.ok).length / recent.length;
    const avgRt = recent.reduce((a, b) => a + b.rt, 0) / recent.length;
    const speed = Math.max(0, Math.min(1, (2000 - avgRt) / (2000 - 600)));
    return 0.6 * acc + 0.4 * speed;
  })();

  const scaleLenientToBrisk = (base: number) => {
    const min = 0.8, max = 1.25;
    const factor = max - (max - min) * skillScore;
    return Math.round(base * factor);
  };
  const randomAdaptiveDurationMs = () => {
    const min = 24000, max = 46000;
    const base = Math.floor(Math.random() * (max - min + 1)) + min;
    return scaleLenientToBrisk(base);
  };
  const adaptivePromptIdleTimeout = () => scaleLenientToBrisk(BASE_PROMPT_IDLE_TIMEOUT_MS);
  const adaptiveHintDelay = () => scaleLenientToBrisk(BASE_HINT_DELAY_MS);

  // ---------- Sounds ----------
  const [soundOn, setSoundOn] = useState<boolean>(true);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const ensureAudioReady = () => {
    if (!soundOn) return;
    if (!audioCtxRef.current) {
      const ctx = makeAudio();
      if (ctx) audioCtxRef.current = ctx;
    } else if (audioCtxRef.current?.state === "suspended") {
      audioCtxRef.current.resume().catch(() => {});
    }
  };
  const beepCorrect = () => { if (soundOn && audioCtxRef.current) playTone(audioCtxRef.current, 880, 120, "sine"); };
  const thudWrong  = () => { if (soundOn && audioCtxRef.current) playTone(audioCtxRef.current, 220, 140, "square"); };

  // ---------- Timers / Refs ----------
  const startBtnRef = useRef<HTMLButtonElement | null>(null);
  const beginBtnRef = useRef<HTMLButtonElement | null>(null);
  const liveRef = useRef<HTMLDivElement | null>(null);

  const hintTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const promptIdleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const promptCooldownRef = useRef<boolean>(false);

  const adventureDurationRef = useRef<number>(0);
  const adventureTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ---------- Utilities ----------
  const announce = (text: string) => {
    setMessage(text);
    const node = liveRef.current;
    if (!node) return;
    node.textContent = "";
    setTimeout(() => { node.textContent = text; }, 20);
  };

  const remainingTargets = (c: Record<Target["code"], number>) =>
    TARGETS.filter(t => (c[t.code] ?? 0) < TARGET_TIMES);
  const pickNextTarget = (c: Record<Target["code"], number>): Target | null => {
    const pool = remainingTargets(c);
    if (pool.length === 0) return null;
    return pool[Math.floor(Math.random() * pool.length)];
  };
  const describeProgress = (c: Record<Target["code"], number>): string =>
    TARGETS.map(t => `${t.label} ${c[t.code]}/${TARGET_TIMES}`).join(", ");

  const scheduleHint = (target: Target | null) => {
    if (!target) return;
    if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    hintTimerRef.current = setTimeout(() => offerLocationHint(target), adaptiveHintDelay());
  };
  const cancelHint = () => {
    if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    hintTimerRef.current = null;
  };
  const offerLocationHint = (target: Target) => {
    if (target.code === " ") {
      announce("Hint: Space is the long, wide bar along the bottom center of the keyboard. Slide your thumbs down.");
      return;
    }
    switch (target.code) {
      case "ArrowLeft":
        announce("Hint: Move down and to the right. Find the arrow cluster; Left is on the left.");
        break;
      case "ArrowRight":
        announce("Hint: Move down and to the right. Right is on the right of the arrow cluster.");
        break;
      case "ArrowUp":
        announce("Hint: Move down and to the right. Up is the single key above Left and Right.");
        break;
      case "ArrowDown":
        announce("Hint: Move down and to the right. Down is below Up, between Left and Right.");
        break;
    }
  };
  const wrongKeyCoach = (pressedKey: string, target: Target) => {
    const wantSpace = target.code === " ";
    const pressedIsSpace = pressedKey === " " || pressedKey === "Spacebar";
    if (wantSpace && !pressedIsSpace) {
      if (ARROW_SET.has(pressedKey as Target["code"])) {
        announce("Close, but not it. We’re looking for Space, not an arrow. Space is the long bar along the bottom center.");
      } else if (WASD_SET.has(pressedKey)) {
        announce("You’re on W, A, S, D. Slide down to the Space bar at the very bottom.");
      } else {
        announce("Not quite. Aim for Space: a wide bar at the bottom center.");
      }
      thudWrong();
      return;
    }
    if (!wantSpace) {
      if (pressedIsSpace) { announce("That was Space. Find the arrow cluster: bottom-right of most keyboards."); thudWrong(); return; }
      const pk = pressedKey as Target["code"];
      if (ARROW_SET.has(pk)) {
        if (target.code === "ArrowLeft" && pk === "ArrowRight") announce("Other way—press Left Arrow.");
        else if (target.code === "ArrowRight" && pk === "ArrowLeft") announce("Other way—press Right Arrow.");
        else if (target.code === "ArrowUp" && pk === "ArrowDown") announce("Too far down—press Up Arrow.");
        else if (target.code === "ArrowDown" && pk === "ArrowUp") announce("Come down one—press Down Arrow.");
        else announce(`Not that one. We’re looking for the ${target.label}.`);
      } else if (WASD_SET.has(pressedKey)) {
        announce("You’re on W, A, S, D. Move your hand down and to the right for the inverted T arrow cluster.");
      } else {
        announce(`That wasn’t it. Find the ${target.label}. The arrow keys are typically bottom-right.`);
      }
      thudWrong();
    }
  };

  // ---------- Tutorial flow ----------
  const startTutorial = () => {
    ensureAudioReady();
    setPhase("tutorial");
    setStarted(true);
    const fresh: Record<Target["code"], number> = { " ": 0, ArrowLeft: 0, ArrowRight: 0, ArrowUp: 0, ArrowDown: 0 };
    setCounts(fresh);
    const nxt = pickNextTarget(fresh);
    setCurrent(nxt);
    setCanBeginAdventure(false);
    if (nxt) {
      announce(`Tutorial started. Press ${nxt.label}. You must find each key three times, in any order.`);
      scheduleHint(nxt);
    }
  };

  useEffect(() => {
    if (phase !== "tutorial") return;
    const onKeyDown = (e: KeyboardEvent) => {
      ensureAudioReady();
      const norm: string =
        e.key === " " || e.code === "Space" || e.key === "Spacebar" ? " " : e.key;
      if (!current) return;
      if (norm === current.code) {
        setCounts(prev => {
          const next = { ...prev, [current.code]: Math.min(prev[current.code] + 1, TARGET_TIMES) };
          const doneAll = TARGETS.every(t => next[t.code] >= TARGET_TIMES);
          const now = next[current.code];
          if (now < TARGET_TIMES) announce(`Good! ${current.label} ${now}/${TARGET_TIMES}. Progress: ${describeProgress(next)}.`);
          else announce(`Great! ${current.label} complete. Progress: ${describeProgress(next)}.`);
          beepCorrect();
          cancelHint();
          if (doneAll) {
            setCanBeginAdventure(true);
            setCurrent(null);
            setTimeout(() => {
              announce("Tutorial complete. You can begin the adventure when ready.");
              beginBtnRef.current?.focus();
            }, 500);
          } else {
            const nxt = pickNextTarget(next);
            setCurrent(nxt);
            scheduleHint(nxt);
          }
          return next;
        });
      } else {
        wrongKeyCoach(norm, current);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => { window.removeEventListener("keydown", onKeyDown); cancelHint(); };
  }, [phase, current]);

  // ---------- Global helpers ----------
  useEffect(() => {
    const onGlobal = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        if (canBeginAdventure) beginBtnRef.current?.focus();
        else startBtnRef.current?.focus();
      } else if (e.key === "Escape") {
        if (phase !== "idle") startTutorial();
      }
    };
    window.addEventListener("keydown", onGlobal);
    return () => window.removeEventListener("keydown", onGlobal);
  }, [phase, canBeginAdventure]);

  // ---------- Adventure helpers ----------
  const resetAdventureStats = () => { setScore(0); setCorrect(0); setWrong(0); setStreak(0); setBestStreak(0); setRecent([]); };

  const newPrompt = (announceIt = true) => {
    const p = PROMPTS[Math.floor(Math.random() * PROMPTS.length)];
    setAdventurePrompt(p);
    if (announceIt) announce(p.text);
    promptShownAtRef.current = Date.now();

    if (promptIdleTimerRef.current) clearTimeout(promptIdleTimerRef.current);
    promptIdleTimerRef.current = setTimeout(() => {
      if (p.hint) announce(`Hint: \${p.hint}`);
      setTimeout(() => newPrompt(true), 1400);
    }, adaptivePromptIdleTimeout());

    if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    hintTimerRef.current = setTimeout(() => {
      if (p.hint) announce(`Hint: \${p.hint}`);
    }, adaptiveHintDelay());
  };

  const beginAdventure = () => {
    ensureAudioReady();
    if (!canBeginAdventure) { announce("You must finish the tutorial before the exercise begins."); return; }
    setPhase("adventure");
    resetAdventureStats();
    adventureDurationRef.current = randomAdaptiveDurationMs();
    setAdventureTimeLeft(adventureDurationRef.current);
    announce("Adventure starting. Make decisions and react to prompts.");
    newPrompt(true);

    if (adventureTimerRef.current) clearInterval(adventureTimerRef.current);
    const start = Date.now();
    adventureTimerRef.current = setInterval(() => {
      const elapsed = Date.now() - start;
      const left = Math.max(0, adventureDurationRef.current - elapsed);
      setAdventureTimeLeft(left);
      if (left <= 0) {
        if (adventureTimerRef.current) clearInterval(adventureTimerRef.current);
        if (promptIdleTimerRef.current) clearTimeout(promptIdleTimerRef.current);
        if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
        endRound();
      }
    }, 200);
  };

  const endRound = () => { announce("Round complete. Summary ready."); setPhase("summary"); };

  const recordSample = (ok: boolean) => {
    const now = Date.now();
    const rt = promptShownAtRef.current ? now - promptShownAtRef.current : 2000;
    promptShownAtRef.current = null;
    setRecent(prev => {
      const next = [...prev, { rt, ok }];
      if (next.length > 12) next.shift();
      return next;
    });
  };

  const handleAdventureKey = (norm: string) => {
    if (!adventurePrompt || promptCooldownRef.current) return;
    const expected = new Set(adventurePrompt.expect);
    const isCorrect = expected.has(norm as Target["code"]);
    promptCooldownRef.current = true;
    setTimeout(() => { promptCooldownRef.current = false; }, PROMPT_COOLDOWN_MS);

    if (isCorrect) {
      setCorrect(c => c + 1);
      setScore(s => Math.max(0, s + 1));
      setStreak(st => { const cur = st + 1; setBestStreak(b => Math.max(b, cur)); return cur; });
      announce("Nice!");
      beepCorrect();
      recordSample(true);
      newPrompt(false);
      setTimeout(() => { if (adventurePrompt) announce(adventurePrompt.text); }, 10);
    } else {
      setWrong(w => w + 1);
      setScore(s => Math.max(0, s - 1));
      setStreak(0);
      thudWrong();
      if (adventurePrompt.expect.includes(" ") && ARROW_SET.has(norm as Target["code"])) announce("Close—this one needs Space, not an arrow.");
      else if (ARROW_SET.has(adventurePrompt.expect[0]) && norm === " ") announce("Not Space—find the arrow cluster for this one.");
      else if (ARROW_SET.has(norm as Target["code"]) && ARROW_SET.has(adventurePrompt.expect[0]) && norm !== adventurePrompt.expect[0]) {
        const want = adventurePrompt.expect[0];
        if (want === "ArrowLeft" && norm === "ArrowRight") announce("Other way—press Left Arrow.");
        else if (want === "ArrowRight" && norm === "ArrowLeft") announce("Other way—press Right Arrow.");
        else if (want === "ArrowUp" && norm === "ArrowDown") announce("Too far down—press Up Arrow.");
        else if (want === "ArrowDown" && norm === "ArrowUp") announce("Come down one—press Down Arrow.");
        else announce("Not that one—try again.");
      } else {
        announce("Try again.");
      }
      recordSample(false);
    }
  };

  useEffect(() => {
    if (phase !== "adventure") return;
    const onKeyDown = (e: KeyboardEvent) => {
      ensureAudioReady();
      const norm: string =
        e.key === " " || e.code === "Space" || e.key === "Spacebar" ? " " : e.key;
      handleAdventureKey(norm);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      if (adventureTimerRef.current) clearInterval(adventureTimerRef.current);
      if (promptIdleTimerRef.current) clearTimeout(promptIdleTimerRef.current);
      if (hintTimerRef.current) clearTimeout(hintTimerRef.current);
    };
  }, [phase, adventurePrompt]);

  const attempts = correct + wrong;
  const accuracy = attempts ? Math.round((correct / attempts) * 100) : 0;

  const canStart = phase === "idle" || phase === "tutorial" || phase === "summary";

  return (
    <main style={{ maxWidth: 720, margin: "4rem auto", padding: "0 1rem", lineHeight: 1.5 }}>
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>KeyQuest</h1>
      <p style={{marginTop:"0.25rem",opacity:0.8}}>BUILD MARKER: <strong>__KQ_ADAPTIVE_BUILD__</strong></p>
      <p style={{ marginBottom: "1rem" }}>
        Free tutorial first: learn Space and Arrow keys with helpful hints. Once you succeed,
        the exercise (adventure) unlocks. <strong>Round timing adapts to your skill</strong> to keep you sharp.
      </p>

      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center", margin: "1rem 0", flexWrap: "wrap" }}>
        <button
          ref={startBtnRef}
          onClick={startTutorial}
          disabled={!canStart || phase === "adventure"}
          aria-disabled={!canStart || phase === "adventure"}
          style={{ padding: "0.6rem 1rem", fontSize: "1rem", borderRadius: "0.75rem", border: "1px solid #ccc",
                   cursor: (canStart && phase !== "adventure") ? "pointer" : "not-allowed" }}
        >
          {started ? "Restart Tutorial" : "Start Tutorial"}
        </button>

        <button
          ref={beginBtnRef}
          onClick={beginAdventure}
          disabled={!canBeginAdventure || phase === "adventure"}
          aria-disabled={!canBeginAdventure || phase === "adventure"}
          style={{ padding: "0.6rem 1rem", fontSize: "1rem", borderRadius: "0.75rem", border: "1px solid #ccc",
                   cursor: (canBeginAdventure && phase !== "adventure") ? "pointer" : "not-allowed",
                   opacity: canBeginAdventure ? 1 : 0.6 }}
        >
          Begin Adventure (Unlocked after Tutorial)
        </button>

        <label style={{ display:"inline-flex", alignItems:"center", gap:"0.5rem", fontSize:"0.95rem" }}>
          <input
            type="checkbox"
            checked={soundOn}
            onChange={(e) => {
              setSoundOn(e.target.checked);
              if (e.target.checked) ensureAudioReady();
            }}
            aria-label="Toggle sound effects"
          />
          Sounds: {soundOn ? "On" : "Off"}
        </label>

        <span aria-hidden="true" style={{ opacity: 0.75 }}>
          Tip: Enter focuses the next action; Esc restarts the tutorial.
        </span>
      </div>

      <p style={{ fontWeight: 600, marginTop: "0.5rem" }}>
        Status: <span>{message}</span>
      </p>

      <section aria-label="Tutorial Progress" style={{ marginTop: "1rem" }}>
        <strong>Progress:</strong>{" "}
        {TARGETS.map(t => (
          <span key={t.code} style={{ marginRight: "0.75rem" }}>
            {t.label}: {counts[t.code] ?? 0}/{TARGET_TIMES}
            {(counts[t.code] ?? 0) >= TARGET_TIMES ? " ✅" : ""}
          </span>
        ))}
      </section>

      {phase === "adventure" && (
        <section aria-label="Adventure HUD" style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #ddd", borderRadius: "0.75rem" }}>
          <p style={{ margin: 0 }}>
            <strong>Prompt:</strong> {adventurePrompt ? adventurePrompt.text : "…"}
          </p>
          <p style={{ marginTop: "0.5rem" }}>
            <strong>Score:</strong> {score} • <strong>Accuracy:</strong> {accuracy}% • <strong>Streak:</strong> {streak} (Best {bestStreak})
          </p>
          <p style={{ marginTop: "0.5rem", opacity: 0.75 }} aria-hidden="true">
            (Timing adapts automatically to your skill.)
          </p>
        </section>
      )}

      {phase === "summary" && (
        <section aria-label="Round Summary" style={{ marginTop: "1rem", padding: "0.75rem", border: "1px solid #ddd", borderRadius: "0.75rem" }}>
          <h2 style={{ fontSize: "1.25rem", marginBottom: "0.5rem" }}>Round Summary</h2>
          <p><strong>Score:</strong> {score}</p>
          <p><strong>Attempts:</strong> {attempts} (Correct {correct} / Wrong {wrong})</p>
          <p><strong>Accuracy:</strong> {accuracy}%</p>
          <p><strong>Best Streak:</strong> {bestStreak}</p>
          <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
            <button onClick={beginAdventure} style={{ padding: "0.6rem 1rem", borderRadius: "0.75rem", border: "1px solid #ccc" }}>
              Play Again
            </button>
            <button onClick={startTutorial} style={{ padding: "0.6rem 1rem", borderRadius: "0.75rem", border: "1px solid #ccc" }}>
              Revisit Tutorial
            </button>
          </div>
        </section>
      )}

      <div
        ref={liveRef}
        aria-live="polite"
        role="status"
        style={{ position: "absolute", left: "-9999px", width: "1px", height: "1px", overflow: "hidden" }}
      />

      <section aria-label="Game Phase" style={{ marginTop: "1.5rem" }}>
        <strong>Phase:</strong>{" "}
        {phase === "idle" ? "Idle" : phase === "tutorial" ? "Tutorial" : phase === "adventure" ? "Adventure" : "Summary"}
      </section>
    </main>
  );
}




