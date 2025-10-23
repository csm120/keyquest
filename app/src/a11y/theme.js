const KEY = "kq:theme";

function systemTheme() {
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  try {
    localStorage.setItem(KEY, theme);
  } catch {}
  const el = document.querySelector(`input[name="theme"][value="${theme}"]`);
  if (el) el.checked = true;
}

export function initTheme() {
  let theme = systemTheme();
  try {
    const saved = localStorage.getItem(KEY);
    if (saved) theme = saved;
  } catch {}
  applyTheme(theme);

  document.querySelectorAll('input[name="theme"]').forEach(input => {
    input.addEventListener("change", () => applyTheme(input.value));
  });

  try {
    if (!localStorage.getItem(KEY)) {
      const mq = matchMedia("(prefers-color-scheme: dark)");
      mq.addEventListener?.("change", () => applyTheme(systemTheme()));
    }
  } catch {}
}
