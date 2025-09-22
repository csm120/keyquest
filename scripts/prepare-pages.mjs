import { promises as fs } from "node:fs";
import path from "node:path";

const root = path.resolve(".");
const dist = path.join(root, "app", "dist");
await fs.mkdir(dist, { recursive: true });

const version = `pages-${new Date().toISOString()}`;
await fs.writeFile(path.join(dist, "build.json"), JSON.stringify({ version }, null, 2) + "\n", "utf8");

const indexPath = path.join(dist, "index.html");
const fourOhFour = path.join(dist, "404.html");
try {
  const indexHtml = await fs.readFile(indexPath, "utf8");
  await fs.writeFile(fourOhFour, indexHtml, "utf8");
} catch {}

const diag = `<!doctype html>
<meta charset="utf-8">
<title>KeyQuest Diagnostics</title>
<main style="max-width:720px;margin:2rem auto;padding:1rem;line-height:1.5">
  <h1>Diagnostics</h1>
  <p>Checks <code>build.json</code> and prints status, headers, and body.</p>
  <pre id="out" aria-live="polite"></pre>
</main>
<script>
(async () => {
  const out = document.getElementById('out');
  try {
    const url = '/keyquest/build.json?bust=' + Date.now();
    const res = await fetch(url, { cache: 'no-store' });
    let text = '';
    text += 'URL: ' + url + '\\n';
    text += 'status: ' + res.status + '\\n\\nheaders\\n';
    for (const [k,v] of res.headers.entries()) text += k + ': ' + v + '\\n';
    text += '\\nbody\\n\\n' + await res.text();
    out.textContent = text;
  } catch (e) {
    out.textContent = 'Error: ' + e;
  }
})();
</script>
`;
await fs.writeFile(path.join(dist, "_diag.html"), diag, "utf8");
console.log("Stamped:", version);
