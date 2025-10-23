import { initTheme } from "./a11y/theme";
import { updateBuildFooter } from "./build/footer";

function bootGameShell(){
  const root=document.getElementById("game-root")!;
  root.innerHTML = `
    <div class="hud">
      <button id="startBtn" aria-keyshortcuts="Space">Start</button>
      <button id="pauseBtn" disabled aria-keyshortcuts="Space">Pause</button>
      <button id="resetBtn" disabled>Reset</button>
      <output id="timeOut" aria-live="off">00:30</output>
      <output id="wpmOut" aria-live="off"></output>
      <output id="accOut" aria-live="off"></output>
      <div id="prompt"></div>
      <input id="typing" disabled />
    </div>`;
  const start = root.querySelector<HTMLButtonElement>("#startBtn")!;
  const pause = root.querySelector<HTMLButtonElement>("#pauseBtn")!;
  const typing= root.querySelector<HTMLInputElement>("#typing")!;
  const announce = document.getElementById("announce")!;
  let running=false;
  function setRunning(v:boolean){ running=v; start.disabled=v; pause.disabled=!v; typing.disabled=!v; announce.textContent = v ? "Started" : "Paused"; if(v) typing.focus(); }
  start.addEventListener("click",()=>setRunning(true));
  pause.addEventListener("click",()=>setRunning(false));
  document.addEventListener("keydown",(e)=>{ if(e.key===" "){ e.preventDefault(); setRunning(!running); }});
}
function bindSkipLink(){
  const skip=document.querySelector<HTMLAnchorElement>("a.skip-link");
  const target=document.getElementById("game-root")!;
  if(!skip||!target) return;
  skip.addEventListener("click",(e)=>{ e.preventDefault(); target.setAttribute("tabindex","-1"); (target as HTMLElement).focus(); setTimeout(()=>target.removeAttribute("tabindex"),0); });
}
function boot(){ initTheme(); bootGameShell(); bindSkipLink(); updateBuildFooter(); }
document.readyState!=="loading" ? boot() : window.addEventListener("DOMContentLoaded", boot);