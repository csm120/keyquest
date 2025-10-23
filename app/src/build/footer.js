function relTime(when) {
  const diff = when.getTime() - Date.now();
  const abs = Math.abs(diff) / 1000;
  if (abs < 30) return "just now";

  const units = [
    ["year", 31536000],
    ["month", 2592000],
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60]
  ];

  const RTF = typeof Intl !== 'undefined' && 'RelativeTimeFormat' in Intl
    ? new Intl.RelativeTimeFormat(undefined, {numeric: "auto", style: "narrow"})
    : null;

  for (const [unit, seconds] of units) {
    if (abs >= seconds || unit === "minute") {
      const quantity = Math.round(diff / seconds);
      return RTF
        ? RTF.format(quantity, unit)
        : `${Math.max(1, Math.abs(Math.round(diff / 60)))}m ago`;
    }
  }
  return "just now";
}

export async function updateBuildFooter() {
  try {
    const res = await fetch("build.json", {cache: "no-store"});
    if (!res.ok) return;

    const data = await res.json();
    const commit = String(data.commit || "").slice(0, 7) || "unknown";
    const built = new Date(String(data.built || Date.now()));
    const el = document.getElementById("buildInfo");
    if (!el) return;

    let intervalId = null;

    const setText = () => {
      el.textContent = `Deployed ${commit} · ${relTime(built)}`;
      try {
        el.setAttribute("title", built.toLocaleString());
      } catch {}
      el.setAttribute("aria-live", "off");
    };

    setText();
    intervalId = window.setInterval(setText, 60000);

    const cleanup = () => {
      if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
      }
    };

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) cleanup();
    }, {once: true});

    window.addEventListener('beforeunload', cleanup);
  } catch {}
}
