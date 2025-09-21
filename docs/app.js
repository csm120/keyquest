(function(){
"use strict";
const polite=document.getElementById("live-polite"), assertive=document.getElementById("live-assertive");
let last=null, lastAt=0; const RATE=350;
const flush=(el,msg)=>{ el.textContent=""; setTimeout(()=>el.textContent=msg,10); };
const speak=(el,msg)=>{ const now=Date.now(); if(now-lastAt<RATE && msg===last) return; lastAt=now; last=msg; flush(el,msg); };
const say=(m)=>speak(polite,m), shout=(m)=>speak(assertive,m);

// One-time cleanup if any old PWA existed
(async()=>{try{
  if("serviceWorker" in navigator){ (await navigator.serviceWorker.getRegistrations()).forEach(r=>r.unregister().catch(()=>{})); }
  if("caches" in window){ (await caches.keys()).forEach(k=>caches.delete(k).catch(()=>{})); }
}catch{}})();

// Scrub stray “Deployed trigger · … ago”
(function(){const re=/Deployed\s+trigger[\s·]*.*\bago\b/i;
 const run=()=>{ const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); const kills=[]; let n;
   while(n=w.nextNode()){ const t=n.data.trim(); if(re.test(t)) kills.push(n); } kills.forEach(t=>t.remove());
   document.querySelectorAll("footer,.footer,#footer,body > :last-child").forEach(el=>{
     const t=(el.textContent||"").trim(); if(re.test(t)) el.style.display="none";
   });
 };
 if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",run,{once:true}); else run();
 new MutationObserver(run).observe(document.documentElement,{childList:true,subtree:true,characterData:true});
})();

const input=document.getElementById("kq-typing");
const pauseBt=document.getElementById("pauseBtn");
const resumeBt=document.getElementById("resumeBtn");
const status=document.getElementById("status");
const chrome=[document.getElementById("kq-instructions"),document.getElementById("kq-controls"),document.getElementById("kq-statusWrap")];
let typing=true, step="welcome";
const setStatus=(t)=> status.innerHTML="<strong>Status:</strong> "+t;

function applyInert(active){ pauseBt.disabled=!active; resumeBt.disabled=active;
  chrome.forEach(r=>{ if(r===document.getElementById("kq-controls")) return;
    r.inert=!!active; if(active) r.setAttribute("aria-hidden","true"); else r.removeAttribute("aria-hidden"); });
}
function trap(){ if(!typing) return; if(document.activeElement!==input) input.focus(); }
function enter(a){ typing=true; applyInert(true); input.value=""; input.focus(); if(a!==false) shout("Typing mode on. Press Escape to pause."); }
function exit(a){ typing=false; applyInert(false); input.blur(); if(a!==false) shout("Typing paused. Press Enter to resume."); setTimeout(()=>resumeBt.focus(),0); }

function handle(key){
  if(step==="welcome"&&(key===" "||key==="Spacebar")){ step="learn_space"; setStatus("Press Space again."); shout("Step one. Press Space again."); return; }
  if(step==="learn_space"&&(key===" "||key==="Spacebar")){ step="learn_arrows"; setStatus("Press Left Arrow, then Right Arrow."); say("Great. Now press Left Arrow, then Right Arrow."); return; }
  if(step==="learn_arrows"){
    if(key==="ArrowLeft"){ say("Left arrow detected. Now press Right Arrow."); return; }
    if(key==="ArrowRight"){ step="ready"; setStatus("Ready to play."); shout("Tutorial complete. You are ready to play."); return; }
  }
}

async function checkForNewBuild(){
  try{
    const r=await fetch('./build.json?ts='+Date.now(),{cache:'no-store'}); if(!r.ok) return;
    const j=await r.json().catch(()=>null); if(!j||!j.version) return;
    const KEY='kq-build-version', prev=localStorage.getItem(KEY);
    const help=document.getElementById('kq-help');
    if(help && !help.textContent.includes('Build:')) help.insertAdjacentHTML('beforeend',` <span>(Build: <code>${j.version}</code>)</span>`);
    if(prev && prev!==j.version){
      if(!sessionStorage.getItem('kq-updated-once')){ sessionStorage.setItem('kq-updated-once','1'); location.reload(); }
    } else if(!prev){
      localStorage.setItem(KEY,j.version);
    }
  }catch{}
}

document.addEventListener("DOMContentLoaded",()=>{
  shout("Welcome to KeyQuest. Typing mode is on. Press Space to begin the tutorial. Press Escape to pause.");
  setStatus("Press Space to begin the tutorial."); enter(false);

  input.addEventListener("keydown",(e)=>{ input.value=""; if(e.key==="Escape"){ e.preventDefault(); exit(); return; } e.preventDefault(); handle(e.key); });
  document.addEventListener("focusin",trap,true);
  pauseBt.addEventListener("click",()=>exit());
  resumeBt.addEventListener("click",()=>enter());

  checkForNewBuild();
  document.addEventListener("visibilitychange",()=>{ if(document.visibilityState==="visible") checkForNewBuild(); });
});
})();
