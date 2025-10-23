type Theme="light"|"dark"|"high-contrast";
const KEY="kq:theme";
function system():Theme{ return matchMedia("(prefers-color-scheme: dark)").matches ? "dark":"light"; }
export function applyTheme(t:Theme){
  document.documentElement.setAttribute("data-theme",t);
  try{localStorage.setItem(KEY,t);}catch{}
  const el=document.querySelector<HTMLInputElement>(`input[name="theme"][value="${t}"]`); if(el) el.checked=true;
}
export function initTheme(){
  let t:Theme=system();
  try{ const s=localStorage.getItem(KEY) as Theme|null; if(s) t=s; }catch{}
  applyTheme(t);
  document.querySelectorAll<HTMLInputElement>('input[name="theme"]').forEach(i=>{
    i.addEventListener("change",()=>applyTheme(i.value as Theme));
  });
  try{ if(!localStorage.getItem(KEY)){ const mq=matchMedia("(prefers-color-scheme: dark)"); mq.addEventListener?.("change",()=>applyTheme(system())); } }catch{}
}