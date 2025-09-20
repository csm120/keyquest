import { useCallback, useEffect, useRef, useState } from "react";

export type CountdownOpts = {
  durationSec?: number;
  onAnnounce?: (msg: string) => void; // use this to feed LiveRegion
};

export function useCountdown({ durationSec = 30, onAnnounce }: CountdownOpts = {}) {
  const [timeLeft, setTimeLeft] = useState<number>(durationSec);
  const [running, setRunning] = useState<boolean>(false);
  const raf = useRef<number | null>(null);
  const last = useRef<number | null>(null);

  const announce = useCallback((msg: string) => onAnnounce?.(msg), [onAnnounce]);

  const tick = useCallback((now: number) => {
    if (!running) return;
    if (last.current == null) last.current = now;
    const delta = (now - last.current) / 1000;
    last.current = now;

    setTimeLeft((prev) => {
      const next = Math.max(0, prev - delta);
      const nextRounded = Math.ceil(next);

      // Throttled announcements at 30, 20, 10, 5, 4, 3, 2, 1
      if ([30, 20, 10, 5, 4, 3, 2, 1].includes(nextRounded)) {
        announce(`${nextRounded} seconds left`);
      }
      if (next === 0) {
        announce("Time’s up");
        setRunning(false);
      }
      return next;
    });

    raf.current = requestAnimationFrame(tick);
  }, [announce, running]);

  const start = useCallback(() => {
    if (!running) {
      setRunning(true);
      announce("Round started");
      last.current = null;
      raf.current = requestAnimationFrame(tick);
    }
  }, [announce, running, tick]);

  const pause = useCallback(() => {
    if (running) {
      setRunning(false);
      announce("Paused");
      if (raf.current) cancelAnimationFrame(raf.current);
      raf.current = null;
    }
  }, [announce, running]);

  const reset = useCallback(() => {
    if (raf.current) cancelAnimationFrame(raf.current);
    raf.current = null;
    setRunning(false);
    setTimeLeft(durationSec);
    announce("Reset");
  }, [announce, durationSec]);

  useEffect(() => {
    return () => { if (raf.current) cancelAnimationFrame(raf.current); };
  }, []);

  return {
    timeLeft: Math.ceil(timeLeft),
    running,
    start, pause, reset
  };
}
